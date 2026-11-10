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
    """Kelas untuk mengelola bola (pergerakan, kecepatan, efek bola api, dan pantulan)."""

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([1, -1]), -1]
        self.speed = 8
        self.is_fireball = False
        self.brick_streak = 0

        # Membuat bentuk bola (lingkaran) berwarna putih
        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="white",
            outline="gray",
        )
        super(Ball, self).__init__(canvas, item)

    def set_fireball(self, status):
        """Mengubah status bola menjadi Bola Api (merah) atau Normal (putih)."""
        self.is_fireball = status
        color = "#ff3300" if status else "white"
        outline = "yellow" if status else "gray"
        self.canvas.itemconfig(self.item, fill=color, outline=outline)

    def update(self):
        """Mengatur pergerakan bola di setiap frame dan deteksi pantulan dinding."""
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
        """Menangani logika tabrakan bola dengan paddle atau brick."""
        coords = self.get_position()
        if not coords:
            return

        x = (coords[0] + coords[2]) * 0.5
        hit_brick = False

        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                # Reset efek fireball jika bola mengenai paddle
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
                # Jika brick punya shield dan bukan fireball, pantulkan dan buka shield
                if game_object.shield and not self.is_fireball:
                    self.direction[1] *= -1
                    game_object.remove_shield()
                    continue

                hit_brick = True
                self.brick_streak += 1

                # Jika mengenai 3 brick berturut-turut, aktifkan Fireball
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
    """Kelas untuk mengontrol papan (paddle) pemain."""

    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 10
        self.ball = None
        self.speed = 18  # Kecepatan gerak papan dibuat cepat dan lincah
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="#f1c40f",
        )
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def widen(self):
        """Memperlebar ukuran papan sebagai power-up."""
        coords = self.get_position()
        if coords:
            current_width = coords[2] - coords[0]
            if current_width < 140:
                self.canvas.coords(
                    self.item, coords[0] - 25, coords[1], coords[2] + 25, coords[3]
                )

    def reset_size(self, canvas_width):
        """Mengembalikan ukuran papan ke standar saat game di-restart."""
        coords = self.get_position()
        if coords:
            center_x = (coords[0] + coords[2]) * 0.5
            y1, y2 = coords[1], coords[3]
            self.canvas.coords(
                self.item,
                center_x - self.width / 2,
                y1,
                center_x + self.width / 2,
                y2,
            )

    def move(self, direction):
        """Menggerakkan papan ke kiri atau kanan dalam batas layar."""
        coords = self.get_position()
        width = self.canvas.winfo_width()
        offset = direction * self.speed

        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None and self.ball.get_position():
                self.ball.move(offset, 0)


class PowerUp(GameObject):
    """Kelas untuk kapsul power-up yang jatuh dari brick yang hancur."""

    def __init__(self, canvas, x, y, game_ref):
        self.width = 25
        self.height = 12
        self.game_ref = game_ref
        item = canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10, fill="#2ecc71", tags="powerup"
        )
        super(PowerUp, self).__init__(canvas, item)

    def update(self):
        """Membuat power-up bergerak jatuh ke bawah."""
        self.move(0, 4)


class Brick(GameObject):
    """Kelas untuk kotak balok (brick) target hancur."""

    COLORS = {1: "#e74c3c", 2: "#3498db", 3: "#2ecc71", 4: "#9b59b6"}

    def __init__(self, canvas, x, y, hits, shield, game_ref):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.shield = shield
        self.game_ref = game_ref

        color = "#34495e" if shield else Brick.COLORS[hits]
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=color,
            outline="gold" if shield else "",
            width=2 if shield else 1,
            tags="brick",
        )
        super(Brick, self).__init__(canvas, item)

    def remove_shield(self):
        """Menghilangkan perisai baja pada brick."""
        self.shield = False
        self.canvas.itemconfig(
            self.item, fill=Brick.COLORS[self.hits], outline="", width=1
        )

    def hit(self):
        """Mengurangi nyawa brick atau menghancurkannya jika hit habis."""
        if self.shield:
            self.remove_shield()
            return

        self.hits -= 1
        if self.hits == 0:
            coords = self.get_position()
            if coords:
                center_x = (coords[0] + coords[2]) * 0.5
                center_y = (coords[1] + coords[3]) * 0.5

                # Peluang memunculkan Multi-Ball atau Power-Up
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
    """Kelas utama untuk mengatur alur permainan, logika game loop, dan interaksi layar."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(
            self, bg="#2c3e50", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.balls = []
        self.powerups = []
        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.game_running = False
        self.game_over_flag = False

        # Membuat susunan kotak-kotak (brick) yang lebih banyak (5 baris penuh warna & perisai)
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 35, 2, shield=True)  # Baris 1 (Berperisai)
            self.add_brick(x + 37.5, 58, 3, shield=False)  # Baris 2 (Hijau)
            self.add_brick(x + 37.5, 81, 2, shield=False)  # Baris 3 (Biru)
            self.add_brick(x + 37.5, 104, 1, shield=False)  # Baris 4 (Merah)
            self.add_brick(x + 37.5, 127, 1, shield=False)  # Baris 5 (Merah)

        self.hud = None
        self.setup_game()

        self.canvas.focus_set()
        # Bind tombol kontrol gerakan papan & tombol restart 'r'
        self.canvas.bind("<KeyPress-Left>", lambda _: self.paddle.move(-1))
        self.canvas.bind("<KeyPress-Right>", lambda _: self.paddle.move(1))
        self.canvas.bind("r", lambda _: self.restart_game())
        self.canvas.bind("R", lambda _: self.restart_game())

    def setup_game(self):
        """Mengatur persiapan awal sebelum game dimulai atau setelah kehilangan nyawa."""
        self.clear_all_balls()
        self.clear_powerups()
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(
            300, 200, "Press Space to Start\n(Press 'R' to Restart)"
        )
        self.canvas.bind("<space>", lambda _: self.start_game())

    def clear_all_balls(self):
        """Menghapus seluruh bola aktif dari layar."""
        for ball in self.balls:
            ball.delete()
        self.balls.clear()

    def clear_powerups(self):
        """Menghapus seluruh power-up yang sedang jatuh."""
        for p in self.powerups:
            p.delete()
        self.powerups.clear()

    def add_ball(self):
        """Membuat objek bola baru di atas papan."""
        paddle_coords = self.paddle.get_position()
        if paddle_coords:
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            ball = Ball(self.canvas, x, 345)
            self.balls.append(ball)
            self.paddle.set_ball(ball)
            self.items[ball.item] = ball

    def spawn_extra_ball(self, x, y):
        """Memunculkan bola tambahan (Multi-Ball) dari posisi brick yang hancur."""
        extra_ball = Ball(self.canvas, x, y)
        extra_ball.direction = [random.choice([1, -1]), 1]
        self.balls.append(extra_ball)
        self.items[extra_ball.item] = extra_ball

    def spawn_powerup(self, x, y):
        """Memunculkan kapsul power-up penambah ukuran papan."""
        p = PowerUp(self.canvas, x, y, self)
        self.powerups.append(p)
        self.items[p.item] = p

    def add_brick(self, x, y, hits, shield):
        """Menambahkan kotak (brick) ke dalam canvas dan kamus item game."""
        brick = Brick(self.canvas, x, y, hits, shield, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size="24"):
        """Menampilkan teks informasi di layar canvas."""
        font = ("Arial", size, "bold")
        return self.canvas.create_text(
            x, y, text=text, font=font, fill="white", justify="center"
        )

    def update_lives_text(self):
        """Memperbarui teks jumlah nyawa pemain di sudut layar."""
        text = f"Lives: {self.lives}"
        if self.hud is None:
            self.hud = self.draw_text(60, 20, text, "14")
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        """Memulai pergerakan game saat tombol Spasi ditekan."""
        self.canvas.unbind("<space>")
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_running = True
        self.game_over_flag = False
        self.game_loop()

    def restart_game(self):
        """Mereset total permainan dari awal (skor/nyawa kembali penuh)."""
        self.lives = 3
        self.game_running = False
        self.game_over_flag = False
        self.canvas.delete("all")
        self.items = {}
        self.balls = []
        self.powerups = []
        self.hud = None

        # Buat ulang papan
        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        # Buat ulang kotak-kotak (brick)
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 35, 2, shield=True)
            self.add_brick(x + 37.5, 58, 3, shield=False)
            self.add_brick(x + 37.5, 81, 2, shield=False)
            self.add_brick(x + 37.5, 104, 1, shield=False)
            self.add_brick(x + 37.5, 127, 1, shield=False)

        self.setup_game()

    def game_loop(self):
        """Loop utama game yang berjalan terus menerus memperbarui posisi objek."""
        if not self.game_running:
            return

        self.check_collisions()

        # Memperbarui posisi seluruh bola aktif
        for ball in list(self.balls):
            ball.update()
            coords = ball.get_position()
            if coords and coords[3] >= self.height:
                if ball.item in self.items:
                    del self.items[ball.item]
                ball.delete()
                self.balls.remove(ball)

        # Memperbarui posisi power-up yang jatuh
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

        # Kondisi Kemenangan atau Kekalahan
        if num_bricks == 0:
            self.game_running = False
            self.draw_text(
                300, 200, "YOU WIN!\nPress 'R' to Play Again", "28"
            )
        elif len(self.balls) == 0:
            self.lives -= 1
            if self.lives < 0:
                self.game_running = False
                self.draw_text(
                    300,
                    200,
                    "GAME OVER!\nPress 'R' to Try Again",
                    "28",
                )
            else:
                self.game_running = False
                self.after(1000, self.setup_game)
        else:
            self.after(20, self.game_loop)

    def check_collisions(self):
        """Mendeteksi titik tumpang tindih (collision) antara bola dan objek lain."""
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
    root.title("Breakout Game - Ultimate Restart Edition")
    game = Game(root)
    game.mainloop()