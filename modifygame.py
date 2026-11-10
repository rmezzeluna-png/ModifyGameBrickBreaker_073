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


class Ball(GameObject):
    """Kelas untuk mengelola Meteor/Bola Energi (pergerakan, kecepatan, dan pantulan)."""

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([1, -1]), -1]
        self.speed = 8
        self.is_fireball = False
        self.brick_streak = 0

        # Bentuk bola bertema Meteor / Bola Energi bercahaya
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
        """Mengubah status meteor menjadi Super Plasma (merah menyala)."""
        self.is_fireball = status
        color = "#ff0055" if status else "#00ffff"
        outline = "#ffcc00" if status else "#ffffff"
        self.canvas.itemconfig(self.item, fill=color, outline=outline)

    def update(self):
        """Mengatur pergerakan meteor di setiap frame dan deteksi pantulan dinding."""
        coords = self.get_position()
        if not coords:
            return
        width = self.canvas.winfo_width()
        # Pantulan dinding kiri & kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Pantulan dinding atas
        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        """Menangani logika tabrakan meteor dengan pesawat atau asteroid."""
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
    """Kelas untuk mengontrol Pesawat Luar Angkasa (pemain)."""

    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        self.speed = 18  # Gerakan pesawat cepat dan lincah
        # Bentuk pesawat menggunakan balok berteknologi futuristik
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
        """Memperlebar ukuran pesawat sebagai power-up."""
        coords = self.get_position()
        if coords:
            current_width = coords[2] - coords[0]
            if current_width < 140:
                self.canvas.coords(
                    self.item, coords[0] - 25, coords[1], coords[2] + 25, coords[3]
                )

    def move(self, direction):
        """Menggerakkan pesawat ke kiri atau kanan dalam batas layar galaksi."""
        coords = self.get_position()
        width = self.canvas.winfo_width()
        offset = direction * self.speed

        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None and self.ball.get_position():
                self.ball.move(offset, 0)


class PowerUp(GameObject):
    """Kapsul Energi / Upgrade yang jatuh dari asteroid yang hancur."""

    def __init__(self, canvas, x, y, game_ref):
        self.width = 25
        self.height = 12
        self.game_ref = game_ref
        item = canvas.create_oval(
            x - 10,
            y - 10,
            x + 10,
            y + 10,
            fill="#2ecc71",
            outline="#ffffff",
            tags="powerup",
        )
        super(PowerUp, self).__init__(canvas, item)

    def update(self):
        """Membuat kapsul energi jatuh ke bawah."""
        self.move(0, 4)


class Brick(GameObject):
    """Kelas untuk Asteroid / Blok Target luar angkasa."""

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
        """Menghilangkan medan perisai kosmik pada asteroid."""
        self.shield = False
        self.canvas.itemconfig(
            self.item, fill=Brick.COLORS[self.hits], outline="#ffffff", width=1
        )

    def hit(self):
        """Mengurangi daya tahan asteroid atau menghancurkannya."""
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
                if rand_val < 0.20:
                    self.game_ref.spawn_extra_ball(center_x, center_y)
                elif 0.20 <= rand_val < 0.35:
                    self.game_ref.spawn_powerup(center_x, center_y)

            self.delete()
        else:
            self.canvas.itemconfig(
                self.item, fill=Brick.COLORS.get(self.hits, "#222222")
            )


class Game(tk.Frame):
    """Kelas utama pengatur alur game bertema Galaksi Luar Angkasa."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        # Latar belakang gelap luar angkasa
        self.canvas = tk.Canvas(
            self, bg="#050515", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        # Menambahkan efek bintang-bintang kecil di latar belakang
        for _ in range(50):
            bx = random.randint(5, self.width - 5)
            by = random.randint(5, self.height - 5)
            self.canvas.create_oval(
                bx, by, bx + 2, by + 2, fill="white", outline=""
            )

        self.items = {}
        self.balls = []
        self.powerups = []
        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.game_running = False

        # Membuat susunan Asteroid (Brick) yang padat & penuh warna
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 35, 2, shield=True)
            self.add_brick(x + 37.5, 58, 3, shield=False)
            self.add_brick(x + 37.5, 81, 2, shield=False)
            self.add_brick(x + 37.5, 104, 1, shield=False)
            self.add_brick(x + 37.5, 127, 1, shield=False)

        self.hud = None
        self.setup_game()

        self.canvas.focus_set()
        self.canvas.bind("<KeyPress-Left>", lambda _: self.paddle.move(-1))
        self.canvas.bind("<KeyPress-Right>", lambda _: self.paddle.move(1))
        self.canvas.bind("r", lambda _: self.restart_game())
        self.canvas.bind("R", lambda _: self.restart_game())

    def setup_game(self):
        """Persiapan awal permainan galaksi."""
        self.clear_all_balls()
        self.clear_powerups()
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(
            300,
            200,
            "SPACE ARCADE\nPress Space to Launch\n(Press 'R' to Restart)",
        )
        self.canvas.bind("<space>", lambda _: self.start_game())

    def clear_all_balls(self):
        """Membersihkan seluruh meteor di layar."""
        for ball in self.balls:
            ball.delete()
        self.balls.clear()

    def clear_powerups(self):
        """Membersihkan kapsul power-up yang aktif."""
        for p in self.powerups:
            p.delete()
        self.powerups.clear()

    def add_ball(self):
        """Memunculkan meteor baru di atas pesawat."""
        paddle_coords = self.paddle.get_position()
        if paddle_coords:
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            ball = Ball(self.canvas, x, 345)
            self.balls.append(ball)
            self.paddle.set_ball(ball)
            self.items[ball.item] = ball

    def spawn_extra_ball(self, x, y):
        """Membuat meteor tambahan (Multi-Ball)."""
        extra_ball = Ball(self.canvas, x, y)
        extra_ball.direction = [random.choice([1, -1]), 1]
        self.balls.append(extra_ball)
        self.items[extra_ball.item] = extra_ball

    def spawn_powerup(self, x, y):
        """Memunculkan power-up upgrade pesawat."""
        p = PowerUp(self.canvas, x, y, self)
        self.powerups.append(p)
        self.items[p.item] = p

    def add_brick(self, x, y, hits, shield):
        """Menambahkan asteroid target ke galaksi."""
        brick = Brick(self.canvas, x, y, hits, shield, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size="22"):
        """Menampilkan teks bertema futuristik di layar."""
        font = ("Courier", size, "bold")
        return self.canvas.create_text(
            x, y, text=text, font=font, fill="#00ffff", justify="center"
        )

    def update_lives_text(self):
        """Memperbarui informasi sisa nyawa (Shield / Nyawa Pesawat)."""
        text = f"Shields: {self.lives}"
        if self.hud is None:
            self.hud = self.draw_text(70, 20, text, "14")
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        """Memulai misi luar angkasa saat tombol Spasi ditekan."""
        self.canvas.unbind("<space>")
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_running = True
        self.game_loop()

    def restart_game(self):
        """Mereset total permainan galaksi ke awal."""
        self.lives = 3
        self.game_running = False
        self.canvas.delete("all")

        # Gambar ulang latar bintang
        for _ in range(50):
            bx = random.randint(5, self.width - 5)
            by = random.randint(5, self.height - 5)
            self.canvas.create_oval(
                bx, by, bx + 2, by + 2, fill="white", outline=""
            )

        self.items = {}
        self.balls = []
        self.powerups = []
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
        """Loop utama permainan galaksi."""
        if not self.game_running:
            return

        self.check_collisions()

        for ball in list(self.balls):
            ball.update()
            coords = ball.get_position()
            if coords and coords[3] >= self.height:
                if ball.item in self.items:
                    del self.items[ball.item]
                ball.delete()
                self.balls.remove(ball)

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
                    self.paddle.widen()
                    if p.item in self.items:
                        del self.items[p.item]
                    p.delete()
                    self.powerups.remove(p)
                elif p_coords[3] >= self.height:
                    if p.item in self.items:
                        del self.items[p.item]
                    p.delete()
                    self.powerups.remove(p)

        num_bricks = len(self.canvas.find_withtag("brick"))

        if num_bricks == 0:
            self.game_running = False
            self.draw_text(
                300, 200, "MISSION SUCCESS!\nPress 'R' to Replay", "26"
            )
        elif len(self.balls) == 0:
            self.lives -= 1
            if self.lives < 0:
                self.game_running = False
                self.draw_text(
                    300, 200, "GAME OVER!\nPress 'R' to Retry", "26"
                )
            else:
                self.game_running = False
                self.after(1000, self.setup_game)
        else:
            self.after(20, self.game_loop)

    def check_collisions(self):
        """Mendeteksi benturan meteor dengan asteroid dan pesawat."""
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
    root.title("Space Arcade - Galaxy Breakout Edition")
    game = Game(root)
    game.mainloop()