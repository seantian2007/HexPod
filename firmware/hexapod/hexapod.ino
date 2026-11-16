// Stage 7 firmware + stage 8 WiFi / data log (branch dev-code_wifi).
// The ESP32 runs Walker + body IK itself.
// The computer only sends stick values and button events (see code/esp_teleop.py).
//
// Tasks (all on core 1; WiFi/BT stay on core 0):
//   control    prio 3  every 20 ms: command -> Walker -> body_ik -> clamp -> 18 servos
//   comm       prio 2  reads lines from USB serial AND from WiFi UDP, puts commands in a
//                      mailbox and events in a queue
//   report     prio 1  log messages, and a statistics line every 10 s (serial + UDP)
//   telemetry  prio 1  NEW: one data line per control frame while recording (UDP only)
//
// WiFi (NEW): the robot is an access point. Join WIFI_SSID_PREFIX-xxxx with WIFI_PASSWORD,
// the robot is 192.168.4.1, commands go to UDP port 1234. Replies go back to whoever
// sent the last valid packet, so the computer needs no configuration.
//
// Protocol (one line each; serial: 115200 and '\n' terminated; UDP: one line per packet):
//   C,<seq>,<lx>,<ly>,<rx>   sticks after deadzone, -1..1, right/up positive (20 Hz)
//   E,<id>,<x>               button event x, executed once per id (the computer sends
//                            each event 3 times over UDP, see "events" below)
//   E,<x>                    old form, no id (still accepted)
//        x = A stand up / reset   B stop and park   N / P next / previous gait
//            Z zero the commanded odometry (NEW, used by walk_test.py)
//   S                        NEW: reply with one "status ..." log line
//   R,1 / R,0                NEW: start / stop the per-frame data log
//   P,<n>                    NEW: ping, UDP only; answered at once with the same line
// Replies over UDP start with a type letter:
//   L,<text>   a log or statistics line (the same text that goes to serial)
//   H,<names>  column names, sent when recording starts
//   D,<values> one control frame (50 Hz while recording)
//   P,<n>      ping answer
// Each time the walker stops it reports the commanded odometry since stand-up (or the last
// Z): "stopped: odo x=.. y=.. yaw=..", x forward, y left, yaw CCW. Used by walk_test.py.
//
// Safety layers (unchanged):
//   1 command timeout: no valid command for 300 ms -> sticks = 0, Walker settles and stops
//     (this also covers WiFi dropping out or the laptop going to sleep)
//   2 IK failure: keep the last frame, go to HOLD until A
//   3 output clamp: every joint kept in its range and within 3 deg of the last frame
//   4 task watchdog: control task must check in every frame, or the chip restarts after 1 s
//
// States: RELAXED --A--> STANDUP --> RUN --(IK fail)--> HOLD --A--> HOMING --> RUN

#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
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

// ---------------- WiFi (NEW) ----------------
// Change the password before taking the robot anywhere public (8+ characters).
const char* WIFI_SSID_PREFIX = "hexapod";                  // full name: hexapod-<last 4 hex of MAC>
const char* WIFI_PASSWORD = "hexapod1234";
const uint16_t CMD_PORT = 1234;                            // the computer sends here
const int TLM_QUEUE_LEN = 16;                              // frames buffered for the telemetry task

// ---------------- shared data between tasks ----------------
struct Command {
    float lx, ly, rx;
    uint32_t t_ms;            // when it arrived (millis), used by the timeout
};
enum Event : char { EV_A = 'A', EV_B = 'B', EV_NEXT = 'N', EV_PREV = 'P', EV_ZERO = 'Z' };

// One control frame for the data log (NEW). The control task fills it at the end of the
// frame and hands it over without waiting; the telemetry task turns it into text.
struct Frame {
    uint32_t frame;           // frame counter (gaps in the log = frames that were dropped)
    uint32_t t_ms;            // millis() at the start of the frame
    uint16_t frame_us;        // time the control task spent on this frame
    uint8_t state, gait;
    uint8_t stance;           // bit i = leg i (R1..L3) in stance
    uint8_t clamps;           // joints the output clamp changed this frame
    float phase;              // gait cycle progress 0..1
    float cmd[3];             // shaped command: vx, vy (mm/s), w (deg/s)
    float odo[3];             // commanded odometry: x, y (mm), yaw (deg)
    float th[NUM_JOINTS];     // joint angles written to the servos (deg)
};
const char* FRAME_COLUMNS =
    "frame,t_ms,frame_us,state,gait,stance,clamps,phase,vx,vy,w,odo_x,odo_y,odo_yaw,"
    "th0,th1,th2,th3,th4,th5,th6,th7,th8,th9,th10,th11,th12,th13,th14,th15,th16,th17";
const int LOG_LEN = 96;

QueueHandle_t cmd_box;        // length 1 mailbox: always the latest command
QueueHandle_t event_q;        // button events, none may be lost
QueueHandle_t log_q;          // text lines for the report task
QueueHandle_t tlm_q;          // Frame snapshots for the telemetry task (NEW)
volatile bool recording = false;      // set by R,1 / R,0 (comm task), read by control task
volatile uint32_t rec_session = 0;    // +1 each time recording starts (telemetry sends a header)

// Who to send UDP replies to: the sender of the last valid packet (written by comm,
// read by report / telemetry). IP and port must change together, hence the lock.
portMUX_TYPE client_lock = portMUX_INITIALIZER_UNLOCKED;
uint32_t client_ip = 0;       // 0 = nobody yet
uint16_t client_port = 0;

void set_client(IPAddress ip, uint16_t port) {
    portENTER_CRITICAL(&client_lock);
    client_ip = (uint32_t)ip;
    client_port = port;
    portEXIT_CRITICAL(&client_lock);
}

bool get_client(IPAddress* ip, uint16_t* port) {
    portENTER_CRITICAL(&client_lock);
    uint32_t a = client_ip;
    *port = client_port;
    portEXIT_CRITICAL(&client_lock);
    *ip = IPAddress(a);
    return a != 0;
}

// Send one line to the client over UDP. Each task uses its own WiFiUDP object (its own
// socket): sockets are safe to use from different tasks, one object shared by two tasks is not.
void udp_send(WiFiUDP& udp, const char* prefix, const char* text) {
    IPAddress ip;
    uint16_t port;
    if (!get_client(&ip, &port)) return;
    udp.beginPacket(ip, port);
    udp.print(prefix);
    udp.print(text);
    udp.endPacket();
}

// counters: each written by one task, read by the report task (32-bit reads are atomic on ESP32)
uint32_t n_frames = 0, n_overruns = 0, max_frame_us = 0;
uint32_t n_rx_ok = 0, n_rx_bad = 0, n_seq_gaps = 0, n_events_lost = 0;
uint32_t n_timeouts = 0, n_clamps = 0, n_ik_fail = 0;
uint32_t n_udp_rx = 0, n_tlm_sent = 0, n_tlm_drop = 0;   // NEW

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
        uint32_t t_frame_ms = millis();
        esp_task_wdt_reset();
        int frame_clamps = 0;                              // for the data log
        float cmd_log[3] = {0, 0, 0};

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
        bool ev_a = false, ev_b = false, ev_zero = false;
        int gait_step = 0;
        while (xQueueReceive(event_q, &ev, 0) == pdTRUE) {
            if (ev == EV_A) ev_a = true;
            if (ev == EV_B) ev_b = true;
            if (ev == EV_ZERO) ev_zero = true;
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
            frame_clamps = clamp_frame(th, prev, MAX_STEP);
            n_clamps += frame_clamps;
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
            if (ev_zero) {
                odo_x = odo_y = odo_yaw = 0;
                log_msg("odo reset");
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
            memcpy(cmd_log, cmd, sizeof(cmd_log));

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
            frame_clamps = clamp_frame(th, prev, MAX_STEP);   // layer 3
            n_clamps += frame_clamps;
            write_angles(th);
            memcpy(prev, th, sizeof(prev));
            break;
        }
        }

        uint32_t dt_us = micros() - t0;
        if (dt_us > max_frame_us) max_frame_us = dt_us;

        // data log (NEW): copy this frame into the queue without waiting. If the telemetry
        // task is behind and the queue is full, the frame is dropped from the log only.
        if (recording) {
            Frame f;
            f.frame = n_frames;
            f.t_ms = t_frame_ms;
            f.frame_us = (uint16_t)(dt_us > 65535 ? 65535 : dt_us);
            f.state = (uint8_t)state;
            f.gait = (uint8_t)gait;
            f.stance = 0;
            for (int i = 0; i < NUM_LEGS; i++) {
                if (walker.was_stance[i]) f.stance |= (uint8_t)(1 << i);
            }
            f.clamps = (uint8_t)frame_clamps;
            f.phase = (float)walker.phase();
            memcpy(f.cmd, cmd_log, sizeof(f.cmd));
            f.odo[0] = (float)odo_x;
            f.odo[1] = (float)odo_y;
            f.odo[2] = (float)odo_yaw;
            memcpy(f.th, prev, sizeof(f.th));
            if (xQueueSend(tlm_q, &f, 0) != pdTRUE) n_tlm_drop++;
        }
        n_frames++;
    }
}

// ---------------- comm task ----------------
// State kept between lines (only the comm task touches it).
struct CommState {
    uint32_t last_seq = 0;
    bool have_seq = false;
    uint32_t last_event_id = 0;
    bool have_event_id = false;
};

static bool push_event(char ev) {
    if (xQueueSend(event_q, &ev, 0) != pdTRUE) n_events_lost++;
    return true;
}

// Parses one line (see the protocol at the top). Returns false for anything malformed.
bool handle_line(char* line, CommState* cs) {
    char* fields[6];
    int n = 0;
    char* save;
    for (char* tok = strtok_r(line, ",", &save); tok && n < 6; tok = strtok_r(NULL, ",", &save)) {
        fields[n++] = tok;
    }
    if (n == 0) return false;

    // E,<x> (old) and E,<id>,<x> (NEW). The same id arrives up to 3 times over UDP;
    // only the first one is executed. Comparing with the last id is enough because the
    // computer sends the copies of one event back to back.
    if (strcmp(fields[0], "E") == 0 && (n == 2 || n == 3)) {
        const char* x = fields[n - 1];
        if (strlen(x) != 1 || !strchr("ABNPZ", x[0])) return false;
        if (n == 3) {
            char* end;
            uint32_t id = strtoul(fields[1], &end, 10);
            if (*end != '\0') return false;
            // a copy, or a late copy of an older event: ignore. Signed difference, so the
            // id may wrap around 2^32 (the computer counts in ms, ~49 days per wrap).
            if (cs->have_event_id && (int32_t)(id - cs->last_event_id) <= 0) return true;
            cs->last_event_id = id;
            cs->have_event_id = true;
        }
        return push_event(x[0]);
    }

    // S: status (NEW). Answered through the log, so it reaches serial and UDP alike.
    if (strcmp(fields[0], "S") == 0 && n == 1) {
        log_msg("status state=%s gait=%s recording=%d", STATE_NAMES[state], GAITS[gait].name,
                recording ? 1 : 0);
        return true;
    }

    // R,1 / R,0: start / stop the data log (NEW).
    if (strcmp(fields[0], "R") == 0 && n == 2 && strlen(fields[1]) == 1 && strchr("01", fields[1][0])) {
        bool on = fields[1][0] == '1';
        if (on && !recording) {
            xQueueReset(tlm_q);            // start clean
            rec_session++;                 // tells the telemetry task to send the column names
        }
        recording = on;
        log_msg("recording %s", on ? "on" : "off");
        return true;
    }

    // C,<seq>,<lx>,<ly>,<rx>
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
    if (cs->have_seq && seq > cs->last_seq + 1) {
        n_seq_gaps += seq - cs->last_seq - 1;              // lines lost on the way
    }
    cs->last_seq = seq;
    cs->have_seq = true;
    Command c = {v[0], v[1], v[2], millis()};
    xQueueOverwrite(cmd_box, &c);                          // whole command at once
    return true;
}

WiFiUDP udp_cmd;              // comm task only: receives commands, answers pings

void comm_task(void*) {
    char buf[64];
    int len = 0;
    bool too_long = false;
    CommState cs;               // one state for both inputs: they share sequence numbers / ids
    char pkt[96];

    for (;;) {
        // 1. USB serial, exactly as before: bytes until '\n'
        while (Serial.available() > 0) {                   // take what has arrived, never wait for more
            int ch = Serial.read();
            if (ch == '\n') {
                buf[len] = '\0';
                if (!too_long && len > 0 && handle_line(buf, &cs)) {
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

        // 2. WiFi UDP (NEW): one line per packet; read every packet that is waiting
        int size;
        while ((size = udp_cmd.parsePacket()) > 0) {
            n_udp_rx++;
            int got = udp_cmd.read(pkt, sizeof(pkt) - 1);
            if (size >= (int)sizeof(pkt) || got <= 0) {    // too long or empty: drop it
                udp_cmd.flush();
                n_rx_bad++;
                continue;
            }
            pkt[got] = '\0';
            while (got > 0 && (pkt[got - 1] == '\n' || pkt[got - 1] == '\r')) pkt[--got] = '\0';

            if (pkt[0] == 'P' && pkt[1] == ',') {          // ping: answer at once, same text
                udp_cmd.beginPacket(udp_cmd.remoteIP(), udp_cmd.remotePort());
                udp_cmd.print(pkt);
                udp_cmd.endPacket();
                continue;
            }
            set_client(udp_cmd.remoteIP(), udp_cmd.remotePort());   // replies go to the last sender
            if (got > 0 && handle_line(pkt, &cs)) {
                n_rx_ok++;
            } else {
                n_rx_bad++;
            }
        }
        vTaskDelay(1);                                     // block 1 ms, let others run
    }
}

// ---------------- report task ----------------
WiFiUDP udp_log;              // report task only

// Every log line goes to serial (as before) and, if a computer has talked to us over
// WiFi, to that computer as "L,<text>".
void out_line(const char* text) {
    Serial.println(text);
    udp_send(udp_log, "L,", text);
}

void report_task(void*) {
    char msg[LOG_LEN];
    char line[256];
    uint32_t next = millis() + REPORT_MS;
    for (;;) {
        int32_t wait = (int32_t)(next - millis());
        if (wait > 0 && xQueueReceive(log_q, msg, pdMS_TO_TICKS(wait)) == pdTRUE) {
            out_line(msg);
            continue;
        }
        if ((int32_t)(millis() - next) >= 0) {
            uint32_t max_us = max_frame_us;
            max_frame_us = 0;
            snprintf(line, sizeof(line),
                     "T state=%s gait=%s frames=%u overruns=%u max_us=%u rx_ok=%u rx_bad=%u "
                     "gaps=%u ev_lost=%u timeouts=%u clamps=%u ik_fail=%u udp_rx=%u tlm_sent=%u tlm_drop=%u",
                     STATE_NAMES[state], GAITS[gait].name, (unsigned)n_frames, (unsigned)n_overruns,
                     (unsigned)max_us, (unsigned)n_rx_ok, (unsigned)n_rx_bad, (unsigned)n_seq_gaps,
                     (unsigned)n_events_lost, (unsigned)n_timeouts, (unsigned)n_clamps,
                     (unsigned)n_ik_fail, (unsigned)n_udp_rx, (unsigned)n_tlm_sent, (unsigned)n_tlm_drop);
            out_line(line);
            next += REPORT_MS;
        }
    }
}

// ---------------- telemetry task (NEW) ----------------
// Waits for Frame snapshots from the control task and sends each one as a "D,..." line.
// Lowest priority on purpose: formatting 18 floats and waiting for WiFi can take a few ms,
// and none of that may delay the control task. If this task falls behind, the queue fills
// up and the control task drops frames from the log (counted in tlm_drop).
WiFiUDP udp_tlm;              // telemetry task only

void telemetry_task(void*) {
    Frame f;
    char line[400];
    uint32_t header_sent_for = 0;
    for (;;) {
        if (xQueueReceive(tlm_q, &f, portMAX_DELAY) != pdTRUE) {
            continue;
        }
        if (header_sent_for != rec_session) {              // first frame of a new recording
            header_sent_for = rec_session;
            udp_send(udp_tlm, "H,", FRAME_COLUMNS);
        }
        int k = snprintf(line, sizeof(line), "%u,%u,%u,%u,%u,%u,%u,%.4f,%.2f,%.2f,%.2f,%.1f,%.1f,%.2f",
                         (unsigned)f.frame, (unsigned)f.t_ms, (unsigned)f.frame_us, (unsigned)f.state,
                         (unsigned)f.gait, (unsigned)f.stance, (unsigned)f.clamps, (double)f.phase,
                         (double)f.cmd[0], (double)f.cmd[1], (double)f.cmd[2],
                         (double)f.odo[0], (double)f.odo[1], (double)f.odo[2]);
        for (int i = 0; i < NUM_JOINTS && k > 0 && k < (int)sizeof(line); i++) {
            k += snprintf(line + k, sizeof(line) - k, ",%.2f", (double)f.th[i]);
        }
        udp_send(udp_tlm, "D,", line);
        n_tlm_sent++;
    }
}

// ---------------- setup ----------------
void setup() {
    pinMode(OE_LEFT, OUTPUT);
    pinMode(OE_RIGHT, OUTPUT);
    digitalWrite(OE_LEFT, HIGH);                           // outputs off while initialising
    digitalWrite(OE_RIGHT, HIGH);

    Serial.begin(115200);

    // WiFi access point (NEW). Started before the servos are touched; takes ~1 s.
    WiFi.mode(WIFI_AP);
    uint8_t mac[6];
    WiFi.softAPmacAddress(mac);
    char ssid[32];
    snprintf(ssid, sizeof(ssid), "%s-%02X%02X", WIFI_SSID_PREFIX, mac[4], mac[5]);
    bool ap_ok = WiFi.softAP(ssid, WIFI_PASSWORD);
    WiFi.setSleep(false);                                  // no power save: lower, steadier latency
    udp_cmd.begin(CMD_PORT);
    udp_log.begin(CMD_PORT + 1);                           // own sockets for the sending tasks
    udp_tlm.begin(CMD_PORT + 2);
    Serial.printf("WiFi %s: %s  password %s  ip %s  udp port %u\n", ap_ok ? "AP up" : "AP FAILED",
                  ssid, WIFI_PASSWORD, WiFi.softAPIP().toString().c_str(), (unsigned)CMD_PORT);

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
    tlm_q = xQueueCreate(TLM_QUEUE_LEN, sizeof(Frame));

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
    xTaskCreatePinnedToCore(comm_task, "comm", 6144, NULL, 2, NULL, 1);
    xTaskCreatePinnedToCore(report_task, "report", 6144, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(telemetry_task, "telemetry", 6144, NULL, 1, NULL, 1);
}

void loop() {
    vTaskDelete(NULL);         // all work happens in the four tasks
}
