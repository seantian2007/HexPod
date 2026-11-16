// Stage 7 firmware: the ESP32 runs Walker + body IK itself.
// The computer only sends stick values and button events (see code/esp_teleop.py).
//
// Tasks (all on core 1; WiFi/BT stay on core 0):
//   control  prio 3  every 20 ms: command -> Walker -> body_ik -> clamp -> 18 servos
//   comm     prio 2  reads serial lines, puts commands in a mailbox and events in a queue
//   report   prio 1  prints log messages, and a statistics line every 10 s
//
// Serial protocol (115200, one line each, '\n' terminated):
//   C,<seq>,<lx>,<ly>,<rx>   sticks after deadzone, -1..1, right/up positive (20 Hz)
//   E,A  stand up / reset     E,B  stop and park     E,N / E,P  next / previous gait
// Each time the walker stops it reports the commanded odometry since stand-up
// ("stopped: odo x=.. y=.. yaw=..", x forward, y left, yaw CCW), used by walk_test.py.
//
// Safety layers:
//   1 command timeout: no valid command for 300 ms -> sticks = 0, Walker settles and stops
//   2 IK failure: keep the last frame, go to HOLD until A
//   3 output clamp: every joint kept in its range and within 3 deg of the last frame
//   4 task watchdog: control task must check in every frame, or the chip restarts after 1 s
//
// States: RELAXED --A--> STANDUP --> RUN --(IK fail)--> HOLD --A--> HOMING --> RUN

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <esp_task_wdt.h>
#include <esp_system.h>
#include <math.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "src/core/body_ik.h"
#include "src/core/walker.h"
#include "src/core/command.h"
#include "src/core/servo_out.h"

// ---------------- hardware (same as esp32_passing_FINAL) ----------------
Adafruit_PWMServoDriver left = Adafruit_PWMServoDriver(0x40);
Adafruit_PWMServoDriver right = Adafruit_PWMServoDriver(0x41);
const int OE_LEFT = 19, OE_RIGHT = 26;                     // active low
// joint order R1..L3 x (coxa, femur, tibia); first 9 on the right board
const uint8_t CH[NUM_JOINTS] = {10, 9, 8, 13, 14, 15, 7, 6, 5, 1, 2, 3, 5, 6, 7, 9, 8, 10};
const float US_PER_TICK = 20000.0f / 4096.0f;

// ---------------- timing and safety parameters ----------------
const uint32_t PERIOD_MS = 20;
const double DT = 0.02;
const uint32_t CMD_TIMEOUT_MS = 300;
const uint32_t WDT_TIMEOUT_MS = 1000;
const uint32_t REPORT_MS = 10000;
const float MAX_STEP = JOINT_SPEED_LIMIT * 0.02f;          // deg per frame (3 deg at 150 deg/s)
const int STANDUP_FRAMES_PER_SERVO = 3;                    // enable one servo every 60 ms
const int HOMING_FRAMES = 75;                              // 1.5 s from HOLD back to home
const float BODY_HEIGHT = 30.0f;                           // swing height h (mm)

// ---------------- shared data between tasks ----------------
struct Command {
    float lx, ly, rx;
    uint32_t t_ms;            // when it arrived (millis), used by the timeout
};
enum Event : char { EV_A = 'A', EV_B = 'B', EV_NEXT = 'N', EV_PREV = 'P' };
const int LOG_LEN = 96;

QueueHandle_t cmd_box;        // length 1 mailbox: always the latest command
QueueHandle_t event_q;        // button events, none may be lost
QueueHandle_t log_q;          // text lines for the report task

// counters: each written by one task, read by the report task (32-bit reads are atomic on ESP32)
uint32_t n_frames = 0, n_overruns = 0, max_frame_us = 0;
uint32_t n_rx_ok = 0, n_rx_bad = 0, n_seq_gaps = 0, n_events_lost = 0;
uint32_t n_timeouts = 0, n_clamps = 0, n_ik_fail = 0;

enum State { RELAXED, STANDUP, RUN, HOLD, HOMING };
const char* STATE_NAMES[] = {"RELAXED", "STANDUP", "RUN", "HOLD", "HOMING"};
State state = RELAXED;
Gait gait = TRIPOD;

void log_msg(const char* fmt, ...) {
    char msg[LOG_LEN];
    va_list args;
    va_start(args, fmt);
    vsnprintf(msg, sizeof(msg), fmt, args);
    va_end(args);
    xQueueSend(log_q, msg, 0);                             // never wait; drop if full
}

// ---------------- servo output ----------------
void write_servo(int i, float us) {
    if (us < 500.0f || us > 2500.0f) {                     // last check, should never trigger
        return;
    }
    uint16_t ticks = (uint16_t)lroundf(us / US_PER_TICK);
    (i < 9 ? right : left).setPWM(CH[i], 0, ticks);
}

void write_angles(const float th[NUM_JOINTS]) {
    float us[NUM_JOINTS];
    angles_to_pulses(th, us);
    for (int i = 0; i < NUM_JOINTS; i++) {
        write_servo(i, us[i]);
    }
}

void relax_all() {
    for (int i = 0; i < NUM_JOINTS; i++) {
        (i < 9 ? right : left).setPWM(CH[i], 0, 4096);    // 4096 = fully off
    }
}

// ---------------- control task ----------------
Walker walker(TRIPOD, GAIT_CFG[TRIPOD].T, BODY_HEIGHT);
CommandShaper shaper;
float HOME[NUM_JOINTS];
float prev[NUM_JOINTS];        // last angles written to the servos

void control_task(void*) {
    esp_task_wdt_add(NULL);                                // layer 4: watch this task
    int pending_gait = -1;     // gait change waiting for the walker to stop
    bool parked = false;       // after B: ignore sticks until A
    bool was_fresh = false;
    double odo_x = 0, odo_y = 0, odo_yaw = 0;   // commanded body motion since stand-up (mm, mm, deg)
    int counter = 0;           // frames spent in STANDUP / HOMING
    float hold_from[NUM_JOINTS];
    const float zero_pose[6] = {0, 0, 0, 0, 0, 0};

    TickType_t wake = xTaskGetTickCount();
    for (;;) {
        if (xTaskDelayUntil(&wake, pdMS_TO_TICKS(PERIOD_MS)) == pdFALSE) {
            n_overruns++;                                  // we were already late
        }
        uint32_t t0 = micros();
        esp_task_wdt_reset();

        // latest command; layer 1: too old -> sticks = 0
        Command c;
        bool fresh = xQueuePeek(cmd_box, &c, 0) == pdTRUE && millis() - c.t_ms <= CMD_TIMEOUT_MS;
        if (was_fresh && !fresh) {
            n_timeouts++;
            log_msg("timeout: no command for %u ms, stopping", (unsigned)CMD_TIMEOUT_MS);
        }
        was_fresh = fresh;
        if (!fresh) {
            c.lx = c.ly = c.rx = 0.0f;
        }

        // button events for this frame
        char ev;
        bool ev_a = false, ev_b = false;
        int gait_step = 0;
        while (xQueueReceive(event_q, &ev, 0) == pdTRUE) {
            if (ev == EV_A) ev_a = true;
            if (ev == EV_B) ev_b = true;
            if (ev == EV_NEXT) gait_step = 1;
            if (ev == EV_PREV) gait_step = -1;
        }

        switch (state) {
        case RELAXED:
            if (ev_a) {
                state = STANDUP;
                counter = 0;
                log_msg("state STANDUP");
            }
            break;

        case STANDUP:                                      // switch servos on one by one
            if (counter % STANDUP_FRAMES_PER_SERVO == 0) {
                int i = counter / STANDUP_FRAMES_PER_SERVO;
                float us[NUM_JOINTS];
                angles_to_pulses(HOME, us);
                write_servo(i, us[i]);
            }
            counter++;
            if (counter >= NUM_JOINTS * STANDUP_FRAMES_PER_SERVO) {
                memcpy(prev, HOME, sizeof(prev));
                walker = Walker(gait, GAIT_CFG[gait].T, BODY_HEIGHT);
                shaper.reset();
                parked = false;
                pending_gait = -1;
                odo_x = odo_y = odo_yaw = 0;
                state = RUN;
                log_msg("state RUN, gait %s", GAITS[gait].name);
            }
            break;

        case HOMING: {                                     // straight line in joint space
            counter++;
            float k = (float)counter / HOMING_FRAMES;
            float th[NUM_JOINTS];
            for (int i = 0; i < NUM_JOINTS; i++) {
                th[i] = hold_from[i] + k * (HOME[i] - hold_from[i]);
            }
            n_clamps += clamp_frame(th, prev, MAX_STEP);
            write_angles(th);
            memcpy(prev, th, sizeof(prev));
            if (counter >= HOMING_FRAMES) {
                walker = Walker(gait, GAIT_CFG[gait].T, BODY_HEIGHT);
                shaper.reset();
                parked = false;
                pending_gait = -1;
                odo_x = odo_y = odo_yaw = 0;
                state = RUN;
                log_msg("state RUN, gait %s", GAITS[gait].name);
            }
            break;
        }

        case HOLD:                                         // keep the last frame until A
            if (ev_a) {
                memcpy(hold_from, prev, sizeof(prev));
                counter = 0;
                state = HOMING;
                log_msg("state HOMING");
            }
            break;

        case RUN: {
            if (ev_a && parked) {
                parked = false;
                log_msg("unparked");
            }
            if (ev_b && !parked) {
                parked = true;
                log_msg("parked: stopping, press A to walk again");
            }

            // same order as one frame of telop.py (checked by test/golden_walk.py)
            float cmd[3];
            if (pending_gait >= 0 || parked) {
                shaper.shape(0, 0, 0, (float)DT, cmd);
            } else {
                shaper.shape(c.lx, c.ly, c.rx, (float)DT, cmd);
            }
            if (gait_step != 0 && pending_gait < 0) {
                pending_gait = ((int)gait + gait_step + NUM_GAITS) % NUM_GAITS;
                log_msg("switching to %s once all feet are down", GAITS[pending_gait].name);
            }
            if (pending_gait >= 0 && walker.stopped) {
                gait = (Gait)pending_gait;
                walker.set_gait(gait, GAIT_CFG[gait].T);
                shaper.set_gait(gait);
                pending_gait = -1;
                log_msg("gait %s, v_max %.0f mm/s, w_max %.1f deg/s",
                        GAITS[gait].name, (double)shaper.v_max, (double)shaper.w_max);
            }

            float feet[NUM_LEGS][3], th6[NUM_LEGS][3];
            int status[NUM_LEGS];
            bool was_stopped = walker.stopped;
            walker.step(cmd[0], cmd[1], cmd[2], DT, feet);

            // commanded odometry: the stance feet push the body by exactly cmd * dt
            if (!(was_stopped && walker.stopped)) {
                double yaw = odo_yaw * M_PI / 180.0;
                double vx = cmd[0], vy = cmd[1], w = cmd[2];
                odo_x += (vx * cos(yaw) - vy * sin(yaw)) * DT;
                odo_y += (vx * sin(yaw) + vy * cos(yaw)) * DT;
                odo_yaw += w * DT;
            }
            if (!was_stopped && walker.stopped) {
                log_msg("stopped: odo x=%.1f mm y=%.1f mm yaw=%.1f deg", odo_x, odo_y, odo_yaw);
            }

            if (!body_ik(zero_pose, feet, th6, status)) {  // layer 2
                n_ik_fail++;
                for (int i = 0; i < NUM_LEGS; i++) {
                    if (status[i] != IK_OK) {
                        log_msg("HOLD: IK failed on leg %d, code %d", i, status[i]);
                        break;
                    }
                }
                state = HOLD;
                break;
            }
            float th[NUM_JOINTS];
            memcpy(th, th6, sizeof(th));
            n_clamps += clamp_frame(th, prev, MAX_STEP);   // layer 3
            write_angles(th);
            memcpy(prev, th, sizeof(prev));
            break;
        }
        }

        uint32_t dt_us = micros() - t0;
        if (dt_us > max_frame_us) max_frame_us = dt_us;
        n_frames++;
    }
}

// ---------------- comm task ----------------
// Parses "C,seq,lx,ly,rx" or "E,x". Returns false for anything malformed.
bool handle_line(char* line, uint32_t* last_seq, bool* have_seq) {
    char* fields[6];
    int n = 0;
    char* save;
    for (char* tok = strtok_r(line, ",", &save); tok && n < 6; tok = strtok_r(NULL, ",", &save)) {
        fields[n++] = tok;
    }
    if (n == 2 && strcmp(fields[0], "E") == 0 && strlen(fields[1]) == 1 && strchr("ABNP", fields[1][0])) {
        char ev = fields[1][0];
        if (xQueueSend(event_q, &ev, 0) != pdTRUE) n_events_lost++;
        return true;
    }
    if (n != 5 || strcmp(fields[0], "C") != 0) {
        return false;
    }
    char* end;
    uint32_t seq = strtoul(fields[1], &end, 10);
    if (*end != '\0') return false;
    float v[3];
    for (int k = 0; k < 3; k++) {
        v[k] = strtof(fields[2 + k], &end);
        if (*end != '\0' || !isfinite(v[k]) || fabsf(v[k]) > 1.001f) return false;
    }
    if (*have_seq && seq > *last_seq + 1) {
        n_seq_gaps += seq - *last_seq - 1;                 // lines lost on the way
    }
    *last_seq = seq;
    *have_seq = true;
    Command c = {v[0], v[1], v[2], millis()};
    xQueueOverwrite(cmd_box, &c);                          // whole command at once
    return true;
}

void comm_task(void*) {
    char buf[64];
    int len = 0;
    bool too_long = false;
    uint32_t last_seq = 0;
    bool have_seq = false;
    for (;;) {
        while (Serial.available() > 0) {                   // take what has arrived, never wait for more
            int ch = Serial.read();
            if (ch == '\n') {
                buf[len] = '\0';
                if (!too_long && len > 0 && handle_line(buf, &last_seq, &have_seq)) {
                    n_rx_ok++;
                } else {
                    n_rx_bad++;
                }
                len = 0;
                too_long = false;
            } else if (ch != '\r') {
                if (len < (int)sizeof(buf) - 1) buf[len++] = (char)ch;
                else too_long = true;
            }
        }
        vTaskDelay(1);                                     // block 1 ms, let others run
    }
}

// ---------------- report task ----------------
void report_task(void*) {
    char msg[LOG_LEN];
    uint32_t next = millis() + REPORT_MS;
    for (;;) {
        int32_t wait = (int32_t)(next - millis());
        if (wait > 0 && xQueueReceive(log_q, msg, pdMS_TO_TICKS(wait)) == pdTRUE) {
            Serial.println(msg);
            continue;
        }
        if ((int32_t)(millis() - next) >= 0) {
            uint32_t max_us = max_frame_us;
            max_frame_us = 0;
            Serial.printf("T state=%s gait=%s frames=%u overruns=%u max_us=%u rx_ok=%u rx_bad=%u "
                          "gaps=%u ev_lost=%u timeouts=%u clamps=%u ik_fail=%u\n",
                          STATE_NAMES[state], GAITS[gait].name, (unsigned)n_frames, (unsigned)n_overruns,
                          (unsigned)max_us, (unsigned)n_rx_ok, (unsigned)n_rx_bad, (unsigned)n_seq_gaps,
                          (unsigned)n_events_lost, (unsigned)n_timeouts, (unsigned)n_clamps,
                          (unsigned)n_ik_fail);
            next += REPORT_MS;
        }
    }
}

// ---------------- setup ----------------
void setup() {
    pinMode(OE_LEFT, OUTPUT);
    pinMode(OE_RIGHT, OUTPUT);
    digitalWrite(OE_LEFT, HIGH);                           // outputs off while initialising
    digitalWrite(OE_RIGHT, HIGH);

    Serial.begin(115200);
    Wire.begin();
    left.begin();
    left.setOscillatorFrequency(25800000);
    left.setPWMFreq(50);
    right.begin();
    right.setOscillatorFrequency(26000000);
    right.setPWMFreq(50);
    Wire.setClock(400000);
    relax_all();
    digitalWrite(OE_LEFT, LOW);
    digitalWrite(OE_RIGHT, LOW);

    for (int leg = 0; leg < NUM_LEGS; leg++) {
        HOME[3 * leg] = 0.0f;
        HOME[3 * leg + 1] = STAND_FEMUR;
        HOME[3 * leg + 2] = STAND_TIBIA;
    }
    memcpy(prev, HOME, sizeof(prev));

    cmd_box = xQueueCreate(1, sizeof(Command));
    event_q = xQueueCreate(8, sizeof(char));
    log_q = xQueueCreate(16, LOG_LEN);

    // layer 4: 1 s task watchdog (Arduino core 3.x has it running already, so reconfigure)
    esp_task_wdt_config_t wdt = {};
    wdt.timeout_ms = WDT_TIMEOUT_MS;
    wdt.idle_core_mask = 1 << 0;
    wdt.trigger_panic = true;
    if (esp_task_wdt_reconfigure(&wdt) != ESP_OK) {
        esp_task_wdt_init(&wdt);
    }

    if (esp_reset_reason() == ESP_RST_TASK_WDT || esp_reset_reason() == ESP_RST_PANIC) {
        Serial.println("WARNING: restarted by the watchdog / a crash");
    }
    Serial.println("READY: servos relaxed, send E,A (button A) to stand up");

    xTaskCreatePinnedToCore(control_task, "control", 8192, NULL, 3, NULL, 1);
    xTaskCreatePinnedToCore(comm_task, "comm", 4096, NULL, 2, NULL, 1);
    xTaskCreatePinnedToCore(report_task, "report", 4096, NULL, 1, NULL, 1);
}

void loop() {
    vTaskDelete(NULL);         // all work happens in the three tasks
}
