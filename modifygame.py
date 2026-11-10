import random
import tkinter as tk


class GameObject(object):
    """Kelas dasar (parent class) untuk semua objek dalam game seperti bola, paddle, brick, dll."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        """Mengambil koordinat posisi objek [x1, y1, x2, y2] pada canvas."""
        return self.canvas.coords(self.item)

    def move(self, x, y):
        """Menggeser posisi objek sejauh x dan y pada canvas."""
        self.canvas.move(self.item, x, y)

    def delete(self):
        """Menghapus objek dari canvas game."""
        self.canvas.delete(self.item)


class Laser(GameObject):
    """Kelas untuk peluru laser yang ditembakkan oleh pesawat."""

    def __init__(self, canvas, x, y):
        item = canvas.create_rectangle(
            x - 2, y - 10, x + 2, y, fill="#ff0055", outline=""
        )
        super(Laser, self).__init__(canvas, item)

    def update(self):
        """Menggerakkan laser meluncur ke atas."""
        self.move(0, -12)


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
        """Mengubah status meteor menjadi Super Plasma."""
        self.is_fireball = status
        color = "#ff0055" if status else "#00ffff"
        outline = "#ffcc00" if status else "#ffffff"
        self.canvas.itemconfig(self.item, fill=color, outline=outline)

    def update(self):
        """Mengatur pergerakan meteor di setiap frame dan pantulan dinding."""
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

    def collide(self, game_objects):
        """Menangani logika tabrakan meteor."""
        coords = self.get_position()
        if not coords:
            return

        x = (coords[0] + coords[2]) * 0.5
        hit_brick = False

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

            elif isinstance(game_object, Brick):
                if game_object.shield and not self.is_fireball:
                    self.direction[1] *= -1
                    game_object.remove_shield()
                    continue

                hit_brick = True
                self.brick_streak += 1

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

        if len(game_objects) > 1 and not hit_brick and not self.is_fireball:
            self.direction[1] *= -1


class Paddle(GameObject):
    """Kelas untuk mengontrol Pesawat Luar Angkasa dengan gerakan sangat mulus."""

    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        self.speed = 10  # Kecepatan langkah per frame untuk gerakan super mulus
        self.direction_x = 0  # -1 (kiri), 1 (kanan), 0 (diam)

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
        """Memperlebar ukuran pesawat."""
        coords = self.get_position()
        if coords:
            current_width = coords[2] - coords[0]
            if current_width < 140:
                self.canvas.coords(
                    self.item, coords[0] - 20, coords[1], coords[2] + 20, coords[3]
                )

    def update_position(self, canvas_width):
        """Memperbarui posisi pesawat secara kontinu agar gerakannya mulus tanpa jeda."""
        if self.direction_x == 0:
            return

        coords = self.get_position()
        if not coords:
            return

        offset = self.direction_x * self.speed
        # Batasi agar tidak keluar layar
        if coords[0] + offset >= 0 and coords[2] + offset <= canvas_width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None and self.ball.get_position():
                self.ball.move(offset, 0)


class PowerUp(GameObject):
    """Kapsul Upgrade / Addon yang jatuh dari asteroid."""

    def __init__(self, canvas, x, y, game_ref, p_type):
        self.width = 24
        self.height = 12
        self.game_ref = game_ref
        self.p_type = p_type  # 'widen' atau 'laser'

        color = "#2ecc71" if p_type == "widen" else "#ff00ff"
        item = canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10, fill=color, outline="#ffffff"
        )
        super(PowerUp, self).__init__(canvas, item)

    def update(self):
        """Membuat kapsul jatuh ke bawah."""
        self.move(0, 4)


class Brick(GameObject):
    """Kelas untuk Asteroid / Blok Target."""

    COLORS = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#9b59b6"}

    def __init__(self, canvas, x, y, hits, shield, game_ref):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.shield = shield
        self.game_ref = game_ref

        color = "#2c3e50" if shield else Brick.COLORS[hits]
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=color,
            outline="#00ffff" if shield else "#ffffff",
            width=2 if shield else 1,
            tags="brick",
        )
        super(Brick, self).__init__(canvas, item)

    def remove_shield(self):
        """Menghilangkan perisai asteroid."""
        self.shield = False
        self.canvas.itemconfig(
            self.item, fill=Brick.COLORS[self.hits], outline="#ffffff", width=1
        )

    def hit(self):
        """Mengurangi daya tahan asteroid."""
        if self.shield:
            self.remove_shield()
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
                elif 0.15 <= rand_val < 0.28:
                    self.game_ref.spawn_powerup(center_x, center_y, "widen")
                elif 0.28 <= rand_val < 0.38:
                    self.game_ref.spawn_powerup(center_x, center_y, "laser")

            self.delete()
        else:
            self.canvas.itemconfig(
                self.item, fill=Brick.COLORS.get(self.hits, "#222222")
            )


class Game(tk.Frame):
    """Kelas utama pengatur alur game galaksi dengan pergerakan mulus & addon laser."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(
            self, bg="#050515", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        # Latar belakang bintang galaksi
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
        self.has_laser = False  # Status addon laser aktif
        self.laser_timer = 0

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.game_running = False

        # Susunan asteroid
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 35, 2, shield=True)
            self.add_brick(x + 37.5, 58, 3, shield=False)
            self.add_brick(x + 37.5, 81, 2, shield=False)
            self.add_brick(x + 37.5, 104, 1, shield=False)
            self.add_brick(x + 37.5, 127, 1, shield=False)

        self.hud = None
        self.setup_game()

        self.canvas.focus_set()
        # Kontrol tombol Mulus (Key Press & Key Release)
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

        # Tombol tambahan Space untuk menembak laser jika addon aktif, atau start game
        self.canvas.bind("<space>", lambda _: self.handle_space_bar())
        self.canvas.bind("r", lambda _: self.restart_game())
        self.canvas.bind("R", lambda _: self.restart_game())

    def set_paddle_direction(self, direction):
        """Mengatur arah gerak pesawat saat tombol ditekan."""
        self.paddle.direction_x = direction

    def stop_paddle_direction(self, direction):
        """Menghentikan pesawat saat tombol dilepaskan."""
        if self.paddle.direction_x == direction:
            self.paddle.direction_x = 0

    def handle_space_bar(self):
        """Menangani fungsi spasi: memulai game atau menembakkan laser."""
        if not self.game_running:
            self.start_game()
        elif self.has_laser:
            self.shoot_laser()

    def shoot_laser(self):
        """Menembakkan dua peluru laser dari sisi pesawat."""
        p_coords = self.paddle.get_position()
        if p_coords:
            left_x = p_coords[0] + 15
            right_x = p_coords[2] - 15
            y = p_coords[1]

            l1 = Laser(self.canvas, left_x, y)
            l2 = Laser(self.canvas, right_x, y)
            self.lasers.extend([l1, l2])

    def setup_game(self):
        """Persiapan awal permainan."""
        self.clear_all_balls()
        self.clear_powerups()
        self.clear_lasers()
        self.has_laser = False
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(
            300,
            200,
            "SPACE ARCADE (SMOOTH + LASER)\nPress Space to Launch\n(Press 'R' to Restart)",
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

    def add_brick(self, x, y, hits, shield):
        brick = Brick(self.canvas, x, y, hits, shield, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size="20"):
        font = ("Courier", size, "bold")
        return self.canvas.create_text(
            x, y, text=text, font=font, fill="#00ffff", justify="center"
        )

    def update_lives_text(self):
        text = f"Shields: {self.lives}"
        if self.hud is None:
            self.hud = self.draw_text(70, 20, text, "14")
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        """Memulai permainan."""
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_running = True
        self.game_loop()

    def restart_game(self):
        """Mereset total game."""
        self.lives = 3
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
        self.has_laser = False
        self.hud = None

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 35, 2, shield=True)
            self.add_brick(x + 37.5, 58, 3, shield=False)
            self.add_brick(x + 37.5, 81, 2, shield=False)
            self.add_brick(x + 37.5, 104, 1, shield=False)
            self.add_brick(x + 37.5, 127, 1, shield=False)

        self.setup_game()

    def game_loop(self):
        """Loop utama game yang sangat mulus."""
        if not self.game_running:
            return

        # Gerakkan pesawat secara mulus berdasarkan tombol yang ditahan
        self.paddle.update_position(self.width)
        self.check_collisions()

        # Update pergerakan bola
        for ball in list(self.balls):
            ball.update()
            coords = ball.get_position()
            if coords and coords[3] >= self.height:
                ball.delete()
                self.balls.remove(ball)

        # Update pergerakan laser peluru
        for laser in list(self.lasers):
            laser.update()
            l_coords = laser.get_position()
            if not l_coords or l_coords[1] <= 0:
                laser.delete()
                self.lasers.remove(laser)
                continue

            # Deteksi tabrakan laser dengan brick
            overlapping = self.canvas.find_overlapping(*l_coords)
            hit_handled = False
            for item_id in overlapping:
                if item_id in self.items and isinstance(
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

        # Update pergerakan power-up jatuh
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
                    # Efek addon power-up
                    if p.p_type == "widen":
                        self.paddle.widen()
                    elif p.p_type == "laser":
                        self.has_laser = True
                        self.laser_timer = 300  # Durasi laser aktif

                    p.delete()
                    self.powerups.remove(p)
                elif p_coords[3] >= self.height:
                    p.delete()
                    self.powerups.remove(p)

        # Timer durasi laser
        if self.has_laser:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.has_laser = False

        num_bricks = len(self.canvas.find_withtag("brick"))

        if num_bricks == 0:
            self.game_running = False
            self.draw_text(
                300, 200, "MISSION SUCCESS!\nPress 'R' to Replay", "24"
            )
        elif len(self.balls) == 0:
            self.lives -= 1
            if self.lives < 0:
                self.game_running = False
                self.draw_text(
                    300, 200, "GAME OVER!\nPress 'R' to Retry", "24"
                )
            else:
                self.game_running = False
                self.after(1000, self.setup_game)
        else:
            self.after(20, self.game_loop)

    def check_collisions(self):
        """Mendeteksi tabrakan bola."""
        for ball in list(self.balls):
            ball_coords = ball.get_position()
            if not ball_coords:
                continue
            items = self.canvas.find_overlapping(*ball_coords)
            objects = [
                self.items[x]
                for x in items
                if x in self.items and self.items[x] != ball
            ]
            ball.collide(objects)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Space Arcade - Smooth Paddle & Laser Addon")
    game = Game(root)
    game.mainloop()