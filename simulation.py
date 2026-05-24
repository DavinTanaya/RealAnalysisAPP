import os
import sys
import math
import random
import pygame

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kekontinuan Seragam x Collision Detection")
clock = pygame.time.Clock()

BG_DARK = (6, 10, 20)
TEXT_PRIMARY = (232, 237, 245)
TEXT_SECONDARY = (136, 146, 176)
ACCENT_GREEN = (0, 255, 136)
ACCENT_CYAN = (0, 212, 255)
DANGER_RED = (255, 51, 102)
HUD_BG = (13, 19, 33, 200)

try:
    FONT_SANS = pygame.font.SysFont("Inter", 15)
    FONT_MONO = pygame.font.SysFont("Consolas", 13)
    FONT_LARGE = pygame.font.SysFont("Inter", 19, bold=True)
except:
    FONT_SANS = pygame.font.Font(None, 18)
    FONT_MONO = pygame.font.Font(None, 15)
    FONT_LARGE = pygame.font.Font(None, 22)

sprites = {}
assets_dir = "Images"
sprite_names = {
    "background": "background.png",
    "player": "player.png",
    "zombie": "zombie.png",
    "bullet": "bullet.png"
}

images_loaded = True
for key, filename in sprite_names.items():
    path = os.path.join(assets_dir, filename)
    if os.path.exists(path):
        try:
            sprites[key] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading {path}: {e}")
            images_loaded = False
    else:
        print(f"Sprite not found: {path}")
        images_loaded = False

bullet_speed = 800
dt = 0.050
is_continuous_mode = False

is_arena_mode = False
player_speed = 180
zombie_speed = 85
player_pos = [100.0, 225.0]
zombie_pos = [650.0, 225.0]
mouse_pos = (400, 225)

zombie_radius = 25
bullet_radius = 7
combined_radius = zombie_radius + bullet_radius

bullets = []
historical_checks = []
auto_fire = False
auto_fire_timer = 0
auto_fire_delay = 350

stats = {"fired": 0, "hits": 0, "misses": 0, "tunneling": 0}
tunneling_alert_timer = 0

def get_dt_min():
    return (2 * combined_radius) / bullet_speed

def dist_to_segment(p, v, w):
    l2 = (v[0] - w[0])**2 + (v[1] - w[1])**2
    if l2 == 0:
        return math.hypot(p[0] - v[0], p[1] - v[1])
    t = ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2
    t = max(0.0, min(1.0, t))
    projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return math.hypot(p[0] - projection[0], p[1] - projection[1])

def respawn_zombie():
    global zombie_pos
    edge = random.randint(0, 3)
    border_offset = 40
    if edge == 0:
        zombie_pos = [random.randint(150, WIDTH - border_offset), border_offset]
    elif edge == 1:
        zombie_pos = [random.randint(150, WIDTH - border_offset), HEIGHT - border_offset]
    elif edge == 2:
        zombie_pos = [WIDTH - border_offset, random.randint(50, HEIGHT - border_offset)]
    else:
        zombie_pos = [WIDTH - border_offset, random.randint(50, HEIGHT - border_offset)]

def toggle_arena_mode():
    global is_arena_mode, player_pos, zombie_pos
    is_arena_mode = not is_arena_mode
    if is_arena_mode:
        respawn_zombie()
    else:
        player_pos = [100.0, 225.0]
        zombie_pos = [650.0, 225.0]
    reset_stats()

def fire_bullet():
    global bullet_speed, bullets, player_pos, mouse_pos, is_arena_mode
    start_x, start_y = float(player_pos[0]), float(player_pos[1])
    
    if is_arena_mode:
        dx = mouse_pos[0] - player_pos[0]
        dy = mouse_pos[1] - player_pos[1]
        angle = math.atan2(dy, dx)
        vx = math.cos(angle) * bullet_speed
        vy = math.sin(angle) * bullet_speed
        start_x += math.cos(angle) * 35
        start_y += math.sin(angle) * 35
    else:
        vx = float(bullet_speed)
        vy = 0.0
        start_x += 35
        
    bullets.append({
        "x": start_x,
        "y": start_y,
        "prev_x": start_x,
        "prev_y": start_y,
        "vx": vx,
        "vy": vy,
        "checks": [(start_x, start_y)],
        "dt_accumulator": 0.0,
        "status": "active"
    })
    stats["fired"] += 1

def reset_stats():
    global bullets, historical_checks, auto_fire
    bullets.clear()
    historical_checks.clear()
    stats["fired"] = 0
    stats["hits"] = 0
    stats["misses"] = 0
    stats["tunneling"] = 0
    auto_fire = False

def save_historical_checks(checks, is_hit):
    historical_checks.append({
        "points": list(checks),
        "is_hit": is_hit,
        "alpha": 255
    })
    if len(historical_checks) > 8:
        historical_checks.pop(0)

running = True
last_ticks = pygame.time.get_ticks()

while running:
    current_ticks = pygame.time.get_ticks()
    real_dt = (current_ticks - last_ticks) / 1000.0
    last_ticks = current_ticks
    real_dt = min(real_dt, 0.1)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_arena_mode and event.button == 1:
                fire_bullet()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not is_arena_mode:
                    fire_bullet()
            elif event.key == pygame.K_a:
                auto_fire = not auto_fire
            elif event.key == pygame.K_m:
                is_continuous_mode = not is_continuous_mode
            elif event.key == pygame.K_p:
                toggle_arena_mode()
            elif event.key == pygame.K_r:
                reset_stats()
            elif event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        bullet_speed = min(5000, bullet_speed + 20)
    if keys[pygame.K_DOWN]:
        bullet_speed = max(200, bullet_speed - 20)
    if keys[pygame.K_RIGHT]:
        dt = min(0.200, dt + 0.001)
    if keys[pygame.K_LEFT]:
        dt = max(0.005, dt - 0.001)

    if is_arena_mode:
        pdx, pdy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            pdy -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            pdy += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            pdx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            pdx += 1.0

        if pdx != 0.0 and pdy != 0.0:
            pdx *= 0.7071
            pdy *= 0.7071

        player_pos[0] += pdx * player_speed * real_dt
        player_pos[1] += pdy * player_speed * real_dt

        player_pos[0] = max(24.0, min(WIDTH - 24.0, player_pos[0]))
        player_pos[1] = max(24.0, min(HEIGHT - 24.0, player_pos[1]))

        zdx = player_pos[0] - zombie_pos[0]
        zdy = player_pos[1] - zombie_pos[1]
        zdist = math.hypot(zdx, zdy)
        if zdist > 15:
            zombie_pos[0] += (zdx / zdist) * zombie_speed * real_dt
            zombie_pos[1] += (zdy / zdist) * zombie_speed * real_dt

    if auto_fire:
        auto_fire_timer += real_dt * 1000
        if auto_fire_timer >= auto_fire_delay:
            fire_bullet()
            auto_fire_timer = 0

    dt_min = get_dt_min()

    for b in list(bullets):
        if b["status"] != "active":
            continue

        b["dt_accumulator"] += real_dt

        while b["dt_accumulator"] >= dt and b["status"] == "active":
            b["dt_accumulator"] -= dt
            b["prev_x"], b["prev_y"] = b["x"], b["y"]

            if is_continuous_mode:
                substeps = math.ceil(dt / dt_min)
                sub_dt = dt / substeps

                sub_x, sub_y = b["x"], b["y"]
                collision_detected = False

                for _ in range(substeps):
                    next_sub_x = sub_x + b["vx"] * sub_dt
                    next_sub_y = sub_y + b["vy"] * sub_dt
                    b["checks"].append((next_sub_x, next_sub_y))

                    dist = math.hypot(next_sub_x - zombie_pos[0], next_sub_y - zombie_pos[1])
                    if dist <= combined_radius:
                        b["x"], b["y"] = next_sub_x, next_sub_y
                        b["status"] = "hit"
                        stats["hits"] += 1
                        save_historical_checks(b["checks"], True)
                        collision_detected = True
                        if is_arena_mode:
                            respawn_zombie()
                        break

                    sub_x, sub_y = next_sub_x, next_sub_y

                if not collision_detected:
                    b["x"], b["y"] = sub_x, sub_y

            else:
                b["x"] = b["x"] + b["vx"] * dt
                b["y"] = b["y"] + b["vy"] * dt
                b["checks"].append((b["x"], b["y"]))

                dist = math.hypot(b["x"] - zombie_pos[0], b["y"] - zombie_pos[1])
                
                was_inside = math.hypot(b["prev_x"] - zombie_pos[0], b["prev_y"] - zombie_pos[1]) <= combined_radius
                is_inside_now = dist <= combined_radius
                d_min = dist_to_segment(zombie_pos, (b["prev_x"], b["prev_y"]), (b["x"], b["y"]))
                passed_zombie = d_min <= combined_radius and not was_inside and not is_inside_now

                if dist <= combined_radius:
                    b["status"] = "hit"
                    stats["hits"] += 1
                    save_historical_checks(b["checks"], True)
                    if is_arena_mode:
                        respawn_zombie()
                elif passed_zombie:
                    b["status"] = "missed"
                    stats["tunneling"] += 1
                    tunneling_alert_timer = 90
                    save_historical_checks(b["checks"], False)

            if b["x"] < -100 or b["x"] > WIDTH + 100 or b["y"] < -100 or b["y"] > HEIGHT + 100:
                b["status"] = "missed"
                stats["misses"] += 1
                save_historical_checks(b["checks"], False)

    bullets = [b for b in bullets if b["status"] == "active"]

    if images_loaded:
        screen.blit(sprites["background"], (0, 0))
    else:
        screen.fill((28, 61, 28))

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (255, 255, 255, 10), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (255, 255, 255, 10), (0, y), (WIDTH, y))

    boundary_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    boundary_color = ACCENT_GREEN + (20,) if is_continuous_mode else DANGER_RED + (20,)
    pygame.draw.circle(boundary_surf, boundary_color, (int(zombie_pos[0]), int(zombie_pos[1])), combined_radius)
    pygame.draw.circle(boundary_surf, ACCENT_GREEN + (90,) if is_continuous_mode else DANGER_RED + (60,), (int(zombie_pos[0]), int(zombie_pos[1])), combined_radius, 2)
    screen.blit(boundary_surf, (0, 0))

    zdx = player_pos[0] - zombie_pos[0]
    zdy = player_pos[1] - zombie_pos[1]
    zombie_angle_deg = math.degrees(math.atan2(-zdy, zdx))
    if images_loaded:
        zw, zh = sprites["zombie"].get_size()
        rotated_zombie = pygame.transform.rotate(sprites["zombie"], zombie_angle_deg)
        rzw, rzh = rotated_zombie.get_size()
        screen.blit(rotated_zombie, (int(zombie_pos[0] - rzw//2), int(zombie_pos[1] - rzh//2)))
    else:
        pygame.draw.circle(screen, (139, 90, 43), (int(zombie_pos[0]), int(zombie_pos[1])), zombie_radius)

    if is_arena_mode:
        pdx = mouse_pos[0] - player_pos[0]
        pdy = mouse_pos[1] - player_pos[1]
        player_angle_deg = math.degrees(math.atan2(-pdy, pdx))
    else:
        player_angle_deg = 0.0

    if images_loaded:
        pw, ph = sprites["player"].get_size()
        rotated_player = pygame.transform.rotate(sprites["player"], player_angle_deg)
        rpw, rph = rotated_player.get_size()
        screen.blit(rotated_player, (int(player_pos[0] - rpw//2), int(player_pos[1] - rph//2)))
    else:
        pygame.draw.circle(screen, (70, 130, 180), (int(player_pos[0]), int(player_pos[1])), 24)

    for h in list(historical_checks):
        h["alpha"] -= 2.5
        if h["alpha"] <= 0:
            historical_checks.remove(h)
            continue

        color = ACCENT_GREEN if h["is_hit"] else DANGER_RED
        alpha_color = color + (int(h["alpha"]),)

        if len(h["points"]) > 1:
            line_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.lines(line_surf, color + (int(h["alpha"] * 0.5),), False, h["points"], 2)
            screen.blit(line_surf, (0, 0))

        dots_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for pt in h["points"]:
            pygame.draw.circle(dots_surf, alpha_color, (int(pt[0]), int(pt[1])), 4)
            pygame.draw.circle(dots_surf, (255, 255, 255, int(h["alpha"] * 0.3)), (int(pt[0]), int(pt[1])), 7, 1)
        screen.blit(dots_surf, (0, 0))

    for b in bullets:
        if len(b["checks"]) > 1:
            trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.lines(trail_surf, ACCENT_CYAN + (100,), False, b["checks"], 3)
            screen.blit(trail_surf, (0, 0))

        if images_loaded:
            bw, bh = sprites["bullet"].get_size()
            screen.blit(sprites["bullet"], (int(b["x"] - bw//2), int(b["y"] - bh//2)))
        else:
            pygame.draw.circle(screen, ACCENT_CYAN, (int(b["x"]), int(b["y"])), bullet_radius)

        for pt in b["checks"]:
            pygame.draw.circle(screen, (255, 255, 255), (int(pt[0]), int(pt[1])), 2)

    hud = pygame.Surface((WIDTH, 110), pygame.SRCALPHA)
    hud.fill((13, 19, 33, 230))
    pygame.draw.rect(hud, (255, 255, 255, 20), (0, 0, WIDTH, 110), 1)
    screen.blit(hud, (0, HEIGHT - 110))

    substeps = math.ceil(dt / dt_min) if is_continuous_mode else 1
    hitrate = f"{(stats['hits'] / stats['fired'] * 100):.0f}%" if stats["fired"] > 0 else "—"

    txt_mode_lbl = FONT_SANS.render("MODE DETEKSI:", True, TEXT_SECONDARY)
    mode_str = "CONTINUOUS (UC)" if is_continuous_mode else "NAIVE (DISKRIT)"
    mode_color = ACCENT_GREEN if is_continuous_mode else DANGER_RED
    txt_mode = FONT_LARGE.render(mode_str, True, mode_color)

    screen.blit(txt_mode_lbl, (20, HEIGHT - 100))
    screen.blit(txt_mode, (20, HEIGHT - 82))

    txt_speed = FONT_MONO.render(f"Kecepatan (v): {bullet_speed} px/s  [UP/DOWN]", True, TEXT_PRIMARY)
    txt_dt = FONT_MONO.render(f"Delta T (dt) : {dt:.3f} s  [LEFT/RIGHT]", True, TEXT_PRIMARY)
    txt_dt_min = FONT_MONO.render(f"dt_min (teori): {dt_min:.4f} s (2R/v)", True, TEXT_PRIMARY)
    txt_sub = FONT_MONO.render(f"Sub-steps     : {substeps}  |  Arena Mode: {'ON' if is_arena_mode else 'OFF'} [P]", True, ACCENT_CYAN)

    screen.blit(txt_speed, (240, HEIGHT - 100))
    screen.blit(txt_dt, (240, HEIGHT - 80))
    screen.blit(txt_dt_min, (240, HEIGHT - 60))
    screen.blit(txt_sub, (240, HEIGHT - 40))

    txt_fired = FONT_MONO.render(f"Fired: {stats['fired']}", True, TEXT_PRIMARY)
    txt_hits = FONT_MONO.render(f"Hits : {stats['hits']}", True, ACCENT_GREEN)
    txt_miss = FONT_MONO.render(f"Miss : {stats['tunneling']} (Tunnel)", True, DANGER_RED)
    txt_rate = FONT_LARGE.render(f"Hit Rate: {hitrate}", True, ACCENT_CYAN)

    screen.blit(txt_fired, (540, HEIGHT - 100))
    screen.blit(txt_hits, (540, HEIGHT - 80))
    screen.blit(txt_miss, (540, HEIGHT - 60))
    screen.blit(txt_rate, (540, HEIGHT - 40))

    if is_arena_mode:
        txt_guide = FONT_MONO.render("[LEFT CLICK] Tembak | [WASD] Gerak | [P] Eksperimen Mode | [R] Reset", True, TEXT_SECONDARY)
    else:
        txt_guide = FONT_MONO.render("[SPACE] Tembak | [A] Auto: ON/OFF | [P] Arena Mode | [M] Mode | [R] Reset", True, TEXT_SECONDARY)
    screen.blit(txt_guide, (20, HEIGHT - 24))

    if tunneling_alert_timer > 0:
        tunneling_alert_timer -= 1
        alert_surf = pygame.Surface((380, 32), pygame.SRCALPHA)
        alert_surf.fill((255, 51, 102, 220))
        pygame.draw.rect(alert_surf, (255, 255, 255, 100), (0, 0, 380, 32), 1)

        alert_text = FONT_LARGE.render("TUNNELING TERDETEKSI — Lolos!", True, (255, 255, 255))
        alert_surf.blit(alert_text, (16, 6))
        screen.blit(alert_surf, (WIDTH//2 - 190, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
