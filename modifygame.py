import random
import tkinter as tk


class GameObject(object):
    """Kelas dasar (parent class) untuk semua objek dalam game."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        """Mengambil koordinat objek [x1, y1, x2, y2]."""
        return self.canvas.coords(self.item)

    def move(self, x, y):
        """Menggeser posisi objek sejauh x dan y."""
        self.canvas.move(self.item, x, y)

    def delete(self):
        """Menghapus objek dari canvas."""
        self.canvas.delete(self.item)


class Laser(GameObject):
    """Kelas untuk peluru laser pesawat."""

    def __init__(self, canvas, x, y):
        item = canvas.create_rectangle(
            x - 2, y - 10, x + 2, y, fill="#ff0055", outline=""
        )
        super(Laser, self).__init__(canvas, item)

    def update(self):
        """Menggerakkan laser ke atas."""
        self.move(0, -16)


class Boss(GameObject):
    """Kelas untuk Boss Alien di akhir level."""

    def __init__(self, canvas, width):
        self.width = 160
        self.height = 40
        self.hp = 25
        self.max_hp = 25
        self.direction = 2

        item = canvas.create_rectangle(
            width / 2 - 80,
            40,
            width / 2 + 80,
            80,
            fill="#8e44ad",
            outline="#f39c12",
            width=3,
        )
        self.hp_text = canvas.create_text(
            width / 2, 60, text=f"BOSS HP: {self.hp}", fill="white", font=("Courier", 12, "bold")
        )
        super(Boss, self).__init__(canvas, item)

    def update(self, canvas_width):
        coords = self.get_position()
        if not coords:
            return
        if coords[0] <= 10 or coords[2] >= canvas_width - 10:
            self.direction *= -1
        self.move(self.direction, 0)
        self.canvas.move(self.hp_text, self.direction, 0)

    def hit(self, game_ref):
        self.hp -= 1
        self.canvas.itemconfig(self.hp_text, text=f"BOSS HP: {self.hp}")
        if self.hp <= 0:
            self.canvas.delete(self.hp_text)
            self.delete()
            game_ref.defeat_boss()


class Ball(GameObject):
    """Kelas untuk mengelola Meteor / Bola Energi."""

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([1, -1]), -1]
        self.speed = 8
        self.is_fireball = False
        self.brick_streak = 0

        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="#00ffff",
            outline="#ffffff",
            width=2,
        )
        super(Ball, self).__init__(canvas, item)

    def set_fireball(self, status):
        self.is_fireball = status
        color = "#ff0055" if status else "#00ffff"
        outline = "#ffcc00" if status else "#ffffff"
        self.canvas.itemconfig(self.item, fill=color, outline=outline)

    def update(self):
        coords = self.get_position()
        if not coords:
            return
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects, game_ref):
        coords = self.get_position()
        if not coords:
            return

        x = (coords[0] + coords[2]) * 0.5
        hit_target = False

        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                self.set_fireball(False)
                self.brick_streak = 0
                self.direction[1] = -1

                paddle_coords = game_object.get_position()
                paddle_center = (paddle_coords[0] + paddle_coords[2]) * 0.5
                if x < paddle_center:
                    self.direction[0] = -1
                else:
                    self.direction[0] = 1

            elif isinstance(game_object, Boss):
                game_object.hit(game_ref)
                self.direction[1] *= -1
                hit_target = True

            elif isinstance(game_object, Brick):
                if game_object.shield and not self.is_fireball:
                    self.direction[1] *= -1
                    game_object.remove_shield()
                    continue

                hit_target = True
                self.brick_streak += 1
                game_ref.add_score()

                if self.brick_streak >= 3 and not self.is_fireball:
                    self.set_fireball(True)

                if not self.is_fireball:
                    brick_coords = game_object.get_position()
                    if x > brick_coords[2]:
                        self.direction[0] = 1
                    elif x < brick_coords[0]:
                        self.direction[0] = -1
                    else:
                        self.direction[1] *= -1

                game_object.hit()

        if len(game_objects) > 1 and not hit_target and not self.is_fireball:
            self.direction[1] *= -1


class Paddle(GameObject):
    """Kelas untuk mengontrol Pesawat Luar Angkasa dengan kecepatan tinggi & super mulus."""

    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        self.speed = 16  # Ditingkatkan agar pergerakan jauh lebih cepat & lincah!
        self.direction_x = 0

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="#3498db",
            outline="#00ffff",
            width=2,
        )
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def widen(self):
        coords = self.get_position()
        if coords:
            current_width = coords[2] - coords[0]
            if current_width < 140:
                self.canvas.coords(
                    self.item, coords[0] - 20, coords[1], coords[2] + 20, coords[3]
                )

    def update_position(self, canvas_width):
        """Memperbarui posisi pesawat secara kontinu tanpa jeda patah-patah."""
        if self.direction_x == 0:
            return

        coords = self.get_position()
        if not coords:
            return

        offset = self.direction_x * self.speed
        if coords[0] + offset >= 0 and coords[2] + offset <= canvas_width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None and self.ball.get_position():
                self.ball.move(offset, 0)


class PowerUp(GameObject):
    """Kapsul Upgrade / Addon."""

    def __init__(self, canvas, x, y, game_ref, p_type):
        self.width = 24
        self.height = 12
        self.game_ref = game_ref
        self.p_type = p_type

        colors = {
            "widen": "#2ecc71",
            "laser": "#ff00ff",
            "shield": "#3498db",
            "bomb": "#e74c3c",
        }
        item = canvas.create_oval(
            x - 10,
            y - 10,
            x + 10,
            y + 10,
            fill=colors.get(p_type, "white"),
            outline="#ffffff",
        )
        super(PowerUp, self).__init__(canvas, item)

    def update(self):
        self.move(0, 4)


class Brick(GameObject):
    """Kelas untuk Asteroid / Blok Target."""

    COLORS = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#9b59b6"}

    def __init__(self, canvas, x, y, hits, shield, brick_type, game_ref):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.shield = shield
        self.brick_type = brick_type
        self.game_ref = game_ref

        if brick_type == "bomb":
            color = "#ff3333"
            outline = "yellow"
        elif brick_type == "mystery":
            color = "#1abc9c"
            outline = "white"
        else:
            color = "#2c3e50" if shield else Brick.COLORS[hits]
            outline = "#00ffff" if shield else "#ffffff"

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=color,
            outline=outline,
            width=2 if shield or brick_type != "normal" else 1,
            tags="brick",
        )
        super(Brick, self).__init__(canvas, item)

    def remove_shield(self):
        self.shield = False
        self.canvas.itemconfig(
            self.item, fill=Brick.COLORS[self.hits], outline="#ffffff", width=1
        )

    def hit(self):
        if self.shield:
            self.remove_shield()
            return

        if self.brick_type == "bomb":
            self.game_ref.trigger_bomb(self)
            self.delete()
            return

        if self.brick_type == "mystery":
            self.game_ref.trigger_mystery(self)
            self.delete()
            return

        self.hits -= 1
        if self.hits == 0:
            coords = self.get_position()
            if coords:
                center_x = (coords[0] + coords[2]) * 0.5
                center_y = (coords[1] + coords[3]) * 0.5

                rand_val = random.random()
                if rand_val < 0.15:
                    self.game_ref.spawn_extra_ball(center_x, center_y)
                elif 0.15 <= rand_val < 0.25:
                    self.game_ref.spawn_powerup(center_x, center_y, "widen")
                elif 0.25 <= rand_val < 0.35:
                    self.game_ref.spawn_powerup(center_x, center_y, "laser")
                elif 0.35 <= rand_val < 0.42:
                    self.game_ref.spawn_powerup(center_x, center_y, "shield")
                elif 0.42 <= rand_val < 0.50:
                    self.game_ref.spawn_powerup(center_x, center_y, "bomb")

            self.delete()
        else:
            self.canvas.itemconfig(
                self.item, fill=Brick.COLORS.get(self.hits, "#222222")
            )


class Game(tk.Frame):
    """Kelas utama pengatur alur game galaksi."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.combo = 1
        self.width = 610
        self.height = 400

        self.canvas = tk.Canvas(
            self, bg="#050515", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        for _ in range(50):
            bx = random.randint(5, self.width - 5)
            by = random.randint(5, self.height - 5)
            self.canvas.create_oval(
                bx, by, bx + 2, by + 2, fill="white", outline=""
            )

        self.items = {}
        self.balls = []
        self.powerups = []
        self.lasers = []
        self.boss = None
        self.has_laser = False
        self.laser_timer = 0
        self.shield_active = False
        self.shield_item = None

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.game_running = False
        self.building_bricks()

        self.hud_score = None
        self.hud_lives = None
        self.hud_combo = None

        self.setup_game()

        self.canvas.focus_set()
        # Kontrol tombol responsif super mulus (Key Press & Key Release)
        self.canvas.bind(
            "<KeyPress-Left>", lambda _: self.set_paddle_direction(-1)
        )
        self.canvas.bind(
            "<KeyRelease-Left>", lambda _: self.stop_paddle_direction(-1)
        )
        self.canvas.bind(
            "<KeyPress-Right>", lambda _: self.set_paddle_direction(1)
        )
        self.canvas.bind(
            "<KeyRelease-Right>", lambda _: self.stop_paddle_direction(1)
        )
        self.canvas.bind("<space>", lambda _: self.handle_space_bar())
        self.canvas.bind("r", lambda _: self.restart_game())
        self.canvas.bind("R", lambda _: self.restart_game())

    def building_bricks(self):
        types = ["normal", "bomb", "mystery"]
        for x in range(5, self.width - 5, 75):
            b_type1 = random.choice(types) if x % 150 == 0 else "normal"
            b_type2 = random.choice(types) if x % 225 == 0 else "normal"
            self.add_brick(x + 37.5, 35, 2, shield=True, brick_type="normal")
            self.add_brick(x + 37.5, 58, 3, shield=False, brick_type=b_type1)
            self.add_brick(x + 37.5, 81, 2, shield=False, brick_type="normal")
            self.add_brick(x + 37.5, 104, 1, shield=False, brick_type=b_type2)

    def trigger_bomb(self, brick_obj):
        coords = brick_obj.get_position()
        if not coords:
            return
        cx, cy = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        for item_id, obj in list(self.items.items()):
            if isinstance(obj, Brick) and obj != brick_obj:
                b_coords = obj.get_position()
                if b_coords:
                    bcx = (b_coords[0] + b_coords[2]) / 2
                    bcy = (b_coords[1] + b_coords[3]) / 2
                    if abs(cx - bcx) <= 85 and abs(cy - bcy) <= 30:
                        obj.delete()
                        del self.items[item_id]

    def trigger_mystery(self, brick_obj):
        coords = brick_obj.get_position()
        if coords:
            cx, cy = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
            p_type = random.choice(["widen", "laser", "shield", "bomb"])
            self.spawn_powerup(cx, cy, p_type)

    def set_paddle_direction(self, direction):
        self.paddle.direction_x = direction

    def stop_paddle_direction(self, direction):
        if self.paddle.direction_x == direction:
            self.paddle.direction_x = 0

    def handle_space_bar(self):
        if not self.game_running:
            self.start_game()
        elif self.has_laser:
            self.shoot_laser()

    def shoot_laser(self):
        p_coords = self.paddle.get_position()
        if p_coords:
            l1 = Laser(self.canvas, p_coords[0] + 15, p_coords[1])
            l2 = Laser(self.canvas, p_coords[2] - 15, p_coords[1])
            self.lasers.extend([l1, l2])

    def add_score(self):
        self.score += 10 * self.combo
        self.combo = min(self.combo + 1, 5)
        if self.score > self.high_score:
            self.high_score = self.score
        self.update_hud()

    def update_hud(self):
        if self.hud_score:
            self.canvas.itemconfig(
                self.hud_score,
                text=f"Score: {self.score} (Hi: {self.high_score})",
            )
        if self.hud_lives:
            self.canvas.itemconfig(self.hud_lives, text=f"Shields: {self.lives}")
        if self.hud_combo:
            self.canvas.itemconfig(
                self.hud_combo, text=f"Combo: {self.combo}x"
            )

    def setup_game(self):
        self.clear_all_balls()
        self.clear_powerups()
        self.clear_lasers()
        self.has_laser = False
        self.add_ball()

        if not self.hud_score:
            self.hud_score = self.canvas.create_text(
                110, 20, text=f"Score: 0 (Hi: 0)", fill="#00ffff", font=("Courier", 11, "bold")
            )
            self.hud_lives = self.canvas.create_text(
                280, 20, text=f"Shields: {self.lives}", fill="#00ffff", font=("Courier", 11, "bold")
            )
            self.hud_combo = self.canvas.create_text(
                450, 20, text=f"Combo: 1x", fill="#00ffff", font=("Courier", 11, "bold")
            )
        else:
            self.update_hud()

        self.text = self.canvas.create_text(
            300,
            200,
            text="ULTIMATE SPACE ARCADE\nPress Space to Launch\n(Press 'R' to Restart)",
            fill="#00ffff",
            font=("Courier", 18, "bold"),
            justify="center",
        )

    def clear_all_balls(self):
        for ball in self.balls:
            ball.delete()
        self.balls.clear()

    def clear_powerups(self):
        for p in self.powerups:
            p.delete()
        self.powerups.clear()

    def clear_lasers(self):
        for l in self.lasers:
            l.delete()
        self.lasers.clear()

    def add_ball(self):
        paddle_coords = self.paddle.get_position()
        if paddle_coords:
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            ball = Ball(self.canvas, x, 345)
            self.balls.append(ball)
            self.paddle.set_ball(ball)
            self.items[ball.item] = ball

    def spawn_extra_ball(self, x, y):
        extra_ball = Ball(self.canvas, x, y)
        extra_ball.direction = [random.choice([1, -1]), 1]
        self.balls.append(extra_ball)
        self.items[extra_ball.item] = extra_ball

    def spawn_powerup(self, x, y, p_type):
        p = PowerUp(self.canvas, x, y, self, p_type)
        self.powerups.append(p)

    def add_brick(self, x, y, hits, shield, brick_type):
        brick = Brick(self.canvas, x, y, hits, shield, brick_type, self)
        self.items[brick.item] = brick

    def start_game(self):
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_running = True
        self.game_loop()

    def restart_game(self):
        self.lives = 3
        self.score = 0
        self.combo = 1
        self.game_running = False
        self.canvas.delete("all")

        for _ in range(50):
            bx = random.randint(5, self.width - 5)
            by = random.randint(5, self.height - 5)
            self.canvas.create_oval(
                bx, by, bx + 2, by + 2, fill="white", outline=""
            )

        self.items = {}
        self.balls = []
        self.powerups = []
        self.lasers = []
        self.boss = None
        self.has_laser = False
        self.shield_active = False
        self.hud_score = None
        self.hud_lives = None
        self.hud_combo = None

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.building_bricks()
        self.setup_game()

    def defeat_boss(self):
        self.boss = None
        self.game_running = False
        self.canvas.create_text(
            300, 200, text="MISSION SUCCESS!\nYOU DEFEATED THE BOSS!\nPress 'R' to Replay",
            fill="#f39c12", font=("Courier", 22, "bold"), justify="center", tags="win"
        )

    def game_loop(self):
        if not self.game_running:
            return

        # Perbarui posisi pesawat setiap frame agar sangat responsif & mulus
        self.paddle.update_position(self.width)
        self.check_collisions()

        if self.boss:
            self.boss.update(self.width)

        for ball in list(self.balls):
            ball.update()
            coords = ball.get_position()
            if coords and coords[3] >= self.height:
                if self.shield_active:
                    ball.direction[1] *= -1
                    self.shield_active = False
                    if self.shield_item:
                        self.canvas.delete(self.shield_item)
                        self.shield_item = None
                else:
                    ball.delete()
                    self.balls.remove(ball)
                    self.combo = 1

        for laser in list(self.lasers):
            laser.update()
            l_coords = laser.get_position()
            if not l_coords or l_coords[1] <= 0:
                laser.delete()
                self.lasers.remove(laser)
                continue

            overlapping = self.canvas.find_overlapping(*l_coords)
            hit_handled = False
            for item_id in overlapping:
                if self.boss and item_id == self.boss.item:
                    self.boss.hit(self)
                    laser.delete()
                    self.lasers.remove(laser)
                    hit_handled = True
                    break
                elif item_id in self.items and isinstance(
                    self.items[item_id], Brick
                ):
                    brick_obj = self.items[item_id]
                    brick_obj.hit()
                    laser.delete()
                    self.lasers.remove(laser)
                    hit_handled = True
                    break
            if hit_handled:
                continue

        paddle_coords = self.paddle.get_position()
        for p in list(self.powerups):
            p.update()
            p_coords = p.get_position()
            if p_coords:
                if (
                    paddle_coords
                    and p_coords[3] >= paddle_coords[1]
                    and p_coords[2] >= paddle_coords[0]
                    and p_coords[0] <= paddle_coords[2]
                ):
                    if p.p_type == "widen":
                        self.paddle.widen()
                    elif p.p_type == "laser":
                        self.has_laser = True
                        self.laser_timer = 300
                    elif p.p_type == "shield":
                        self.shield_active = True
                        if self.shield_item:
                            self.canvas.delete(self.shield_item)
                        self.shield_item = self.canvas.create_line(
                            0, 390, self.width, 390, fill="#3498db", width=4
                        )
                    elif p.p_type == "bomb":
                        self.score += 50

                    p.delete()
                    self.powerups.remove(p)
                elif p_coords[3] >= self.height:
                    p.delete()
                    self.powerups.remove(p)

        num_bricks = len(self.canvas.find_withtag("brick"))

        if num_bricks == 0 and not self.boss and self.lives >= 0:
            self.boss = Boss(self.canvas, self.width)

        if len(self.balls) == 0:
            self.lives -= 1
            self.update_hud()
            if self.lives < 0:
                self.game_running = False
                self.canvas.create_text(
                    300, 200, text="GAME OVER!\nPress 'R' to Retry",
                    fill="#ff3333", font=("Courier", 24, "bold"), justify="center"
                )
            else:
                self.game_running = False
                self.after(1000, self.setup_game)
        else:
            # Jeda game loop dipercepat menjadi 15ms untuk kelancaran maksimal (framerate tinggi)
            self.after(15, self.game_loop)

    def check_collisions(self):
        for ball in list(self.balls):
            ball_coords = ball.get_position()
            if not ball_coords:
                continue
            items = self.canvas.find_overlapping(*ball_coords)
            objects = []
            if self.boss and self.boss.item in items:
                objects.append(self.boss)
            for x in items:
                if x in self.items and self.items[x] != ball:
                    objects.append(self.items[x])
            ball.collide(objects, self)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Space Arcade - Ultra Smooth & Fast Paddle Edition")
    game = Game(root)
    game.mainloop()