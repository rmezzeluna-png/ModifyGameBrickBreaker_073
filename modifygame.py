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


class BackgroundStar:
    """Kelas untuk mengelola animasi bintang-bintang di latar belakang luar angkasa."""

    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.choice([1, 1.5, 2])
        self.speed = random.uniform(0.2, 0.8)  # Kecepatan kedip/gerak pelan

        # Membuat titik bintang
        self.item = canvas.create_oval(
            self.x,
            self.y,
            self.x + self.size,
            self.y + self.size,
            fill="white",
            outline="",
            tags="bg_star",
        )
        canvas.tag_lower(self.item)

    def update(self):
        """Menggerakkan bintang perlahan ke bawah untuk efek meluncur di luar angkasa."""
        self.y += self.speed
        if self.y > self.height:
            self.y = 0
            self.x = random.randint(0, self.width)
        self.canvas.coords(
            self.item, self.x, self.y, self.x + self.size, self.y + self.size
        )
        self.canvas.tag_lower(self.item)


class AnimatedRocket:
    """Kelas animasi roket latar belakang yang bergerak menyilang (kiri ke kanan, lalu kanan ke kiri)."""

    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = 1.5  # Kecepatan horizontal (ke kanan/kiri)
        self.dy = -0.8  # Kecepatan vertikal (ke atas)

        # Menggambar komponen bentuk roket
        self.body = canvas.create_polygon(
            0,
            -25,
            -12,
            15,
            12,
            15,
            fill="#ecf0f1",
            outline="#bdc3c7",
            tags="bg_rocket",
        )
        self.window = canvas.create_oval(
            -5, -8, 5, 2, fill="#3498db", outline="#2980b9", tags="bg_rocket"
        )
        self.wing_left = canvas.create_polygon(
            -12, 5, -20, 20, -12, 15, fill="#e74c3c", tags="bg_rocket"
        )
        self.wing_right = canvas.create_polygon(
            12, 5, 20, 20, 12, 15, fill="#e74c3c", tags="bg_rocket"
        )
        self.flame = canvas.create_polygon(
            -6,
            15,
            0,
            30,
            6,
            15,
            fill="#f1c40f",
            outline="#e67e22",
            tags="bg_rocket",
        )

        self.canvas.tag_lower("bg_rocket")

    def update(self):
        """Menggerakkan roket memantul ke kiri dan kanan serta melayang di latar belakang."""
        self.x += self.dx
        self.y += self.dy

        # Pantulan dinding samping kiri dan kanan
        if self.x <= 30 or self.x >= self.width - 30:
            self.dx *= -1

        # Jika roket keluar dari batas atas, reset ke bawah layar dengan posisi acak
        if self.y < -50:
            self.y = self.height + 50
            self.x = random.randint(50, self.width - 50)

        # Efek warna api menyala acak
        flame_color = random.choice(["#f1c40f", "#e67e22", "#e74c3c"])
        self.canvas.itemconfig(self.flame, fill=flame_color)

        # Menggeser seluruh elemen poligon roket secara bersamaan
        items = [
            self.body,
            self.window,
            self.wing_left,
            self.wing_right,
            self.flame,
        ]
        # Untuk menyederhanakan perpindahan koordinat grup, gunakan canvas.move
        for item in items:
            self.canvas.coords(
                item, *[c + (self.x if i % 2 == 0 else self.y) for i, c in enumerate(self.get_relative_coords(item))]
            )
        
        # Cara alternatif yang lebih aman untuk memindah koordinat roket:
        self.redraw_rocket()
        self.canvas.tag_lower("bg_rocket")

    def get_relative_coords(self, item):
        """Mengambil koordinat relatif item."""
        # Fungsi bantu penunjang pergerakan roket
        return [0] * len(self.canvas.coords(item))

    def redraw_rocket(self):
        """Menggambar ulang posisi roket berdasarkan x dan y terbaru."""
        x, y = self.x, self.y
        self.canvas.coords(
            self.body,
            x,
            y - 25,
            x - 12,
            y + 15,
            x + 12,
            y + 15,
        )
        self.canvas.coords(
            self.window, x - 5, y - 8, x + 5, y + 2
        )
        self.canvas.coords(
            self.wing_left,
            x - 12,
            y + 5,
            x - 20,
            y + 20,
            x - 12,
            y + 15,
        )
        self.canvas.coords(
            self.wing_right,
            x + 12,
            y + 5,
            x + 20,
            y + 20,
            x + 12,
            y + 15,
        )
        self.canvas.coords(
            self.flame,
            x - 6,
            y + 15,
            x,
            y + 30,
            x + 6,
            y + 15,
        )


class Laser(GameObject):
    """Kelas untuk peluru laser pesawat."""

    def __init__(self, canvas, x, y):
        item = canvas.create_rectangle(
            x - 2, y - 10, x + 2, y, fill="#ff0055", outline=""
        )
        super(Laser, self).__init__(canvas, item)

    def update(self):
        """Menggerakkan laser ke atas secara cepat."""
        self.move(0, -16)


class Boss(GameObject):
    """Kelas untuk Boss Alien di akhir level."""

    def __init__(self, canvas, width):
        self.width = 160
        self.height = 40
        self.hp = 30
        self.max_hp = 30
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
            width / 2,
            60,
            text=f"BOSS HP: {self.hp}",
            fill="white",
            font=("Courier", 12, "bold"),
        )
        super(Boss, self).__init__(canvas, item)

    def update(self, canvas_width):
        """Menggerakkan boss ke kiri dan kanan."""
        coords = self.get_position()
        if not coords:
            return
        if coords[0] <= 10 or coords[2] >= canvas_width - 10:
            self.direction *= -1
        self.move(self.direction, 0)
        self.canvas.move(self.hp_text, self.direction, 0)

    def hit(self, game_ref):
        """Mengurangi HP boss saat terkena serangan."""
        self.hp -= 1
        self.canvas.itemconfig(self.hp_text, text=f"BOSS HP: {self.hp}")
        if self.hp <= 0:
            self.canvas.delete(self.hp_text)
            self.delete()
            game_ref.defeat_boss()


class Ball(GameObject):
    """Kelas untuk mengelola Meteor/Bola Energi lengkap dengan efek jejak (trail)."""

    def __init__(self, canvas, x, y, speed=6):
        self.radius = 10
        self.direction = [random.choice([1, -1]), -1]
        self.speed = speed
        self.is_fireball = False
        self.brick_streak = 0
        self.trails = []  # Menyimpan daftar elemen visual jejak ekor bola

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
        """Mengubah status bola menjadi Bola Api (Fireball)."""
        self.is_fireball = status
        color = "#ff0055" if status else "#00ffff"
        outline = "#ffcc00" if status else "#ffffff"
        self.canvas.itemconfig(self.item, fill=color, outline=outline)

    def create_trail(self):
        """Membuat lingkaran kecil sebagai efek jejak di belakang bola."""
        coords = self.get_position()
        if not coords:
            return
        cx = (coords[0] + coords[2]) * 0.5
        cy = (coords[1] + coords[3]) * 0.5
        r = self.radius * 0.7

        color = "#ff3300" if self.is_fireball else "#00ffff"
        t_item = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, fill=color, outline=""
        )
        self.canvas.tag_lower(t_item)
        self.trails.append((t_item, 1.0))

    def update_trails(self):
        """Memudarkan dan menghapus jejak ekor bola secara bertahap."""
        new_trails = []
        for t_item, life in self.trails:
            life -= 0.3
            if life <= 0:
                self.canvas.delete(t_item)
            else:
                new_trails.append((t_item, life))
        self.trails = new_trails

    def delete(self):
        """Menghapus bola beserta seluruh jejak trail-nya."""
        for t_item, _ in self.trails:
            self.canvas.delete(t_item)
        self.trails.clear()
        super(Ball, self).delete()

    def update(self):
        """Mengatur pergerakan dan pantulan bola."""
        coords = self.get_position()
        if not coords:
            return

        self.create_trail()
        self.update_trails()

        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects, game_ref):
        """Mendeteksi benturan bola dengan paddle, boss, atau brick."""
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
    """Kelas untuk mengontrol pesawat luar angkasa pemain dengan gerakan sangat mulus."""

    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        self.speed = 16  # Pergerakan cepat dan responsif
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
        """Memperlebar ukuran pesawat sebagai power-up."""
        coords = self.get_position()
        if coords:
            current_width = coords[2] - coords[0]
            if current_width < 140:
                self.canvas.coords(
                    self.item,
                    coords[0] - 20,
                    coords[1],
                    coords[2] + 20,
                    coords[3],
                )

    def update_position(self, canvas_width):
        """Memperbarui posisi pesawat secara kontinu tanpa jeda."""
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
    """Kelas untuk kapsul bonus/upgrade yang jatuh."""

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
        """Membuat kapsul jatuh ke bawah."""
        self.move(0, 4)


class Brick(GameObject):
    """Kelas untuk blok asteroid target."""

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
        """Menghilangkan perisai pelindung asteroid."""
        self.shield = False
        self.canvas.itemconfig(
            self.item, fill=Brick.COLORS[self.hits], outline="#ffffff", width=1
        )

    def hit(self):
        """Mengurangi hit atau menghancurkan asteroid."""
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
    """Kelas utama pengatur alur game galaksi luar angkasa."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.combo = 1
        self.level = 1
        self.max_levels = 3
        self.width = 610
        self.height = 400

        self.canvas = tk.Canvas(
            self, bg="#050515", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        # Membuat latar belakang bintang-bintang luar angkasa
        self.stars = [BackgroundStar(self.canvas, self.width, self.height) for _ in range(60)]
        
        # Membuat animasi roket yang melintas menyilang
        self.rocket = AnimatedRocket(self.canvas, self.width, self.height)

        self.items = {}
        self.balls = []
        self.powerups = []
        self.lasers = []
        self.boss = None
        self.has_laser = False
        self.shield_active = False
        self.shield_item = None
        self.overlay_text = None
        self.title_text = None

        # Variabel animasi teks judul "Revan Mezzeluna"
        self.title_y = 170
        self.title_direction = 1

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.game_running = False
        self.building_bricks_for_level()

        self.hud_score = None
        self.hud_lives = None
        self.hud_combo = None
        self.hud_level = None

        self.setup_game()

        self.canvas.focus_set()
        # Kontrol input keyboard dengan sistem mulus (Key Press & Release)
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

        self.animate_title_loop()

    def animate_title_loop(self):
        """Loop animasi teks 'Revan Mezzeluna' melayang dan berubah warna neon."""
        if not self.game_running and self.title_text:
            self.title_y += 0.3 * self.title_direction
            if abs(self.title_y - 170) > 8:
                self.title_direction *= -1

            self.canvas.coords(self.title_text, 300, self.title_y)
            colors = ["#00ffff", "#ff00ff", "#f1c40f", "#2ecc71"]
            self.canvas.itemconfig(
                self.title_text, fill=random.choice(colors)
            )

        self.after(100, self.animate_title_loop)

    def building_bricks_for_level(self):
        """Membangun pola balok asteroid berdasarkan level permainan."""
        types = ["normal", "bomb", "mystery"]

        if self.level == 1:
            for x in range(5, self.width - 5, 75):
                self.add_brick(
                    x + 37.5, 40, 2, shield=False, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 65, 1, shield=False, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 90, 1, shield=False, brick_type="normal"
                )

        elif self.level == 2:
            for x in range(5, self.width - 5, 75):
                b_type = random.choice(types) if x % 150 == 0 else "normal"
                self.add_brick(
                    x + 37.5, 35, 3, shield=True, brick_type="normal"
                )
                self.add_brick(x + 37.5, 58, 2, shield=False, brick_type=b_type)
                self.add_brick(
                    x + 37.5, 81, 2, shield=False, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 104, 1, shield=False, brick_type="normal"
                )

        elif self.level == 3:
            for x in range(5, self.width - 5, 75):
                b_type1 = random.choice(types) if x % 150 == 0 else "normal"
                b_type2 = random.choice(types) if x % 225 == 0 else "normal"
                self.add_brick(
                    x + 37.5, 35, 3, shield=True, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 58, 3, shield=False, brick_type=b_type1
                )
                self.add_brick(
                    x + 37.5, 81, 2, shield=True, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 104, 1, shield=False, brick_type="normal"
                )
                self.add_brick(
                    x + 37.5, 127, 1, shield=False, brick_type="normal"
                )

    def trigger_bomb(self, brick_obj):
        """Memicu ledakan area berantai dari kotak bom."""
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
        """Memicu kotak misteri untuk menjatuhkan power-up acak."""
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
        """Menangani tombol Spasi untuk mulai atau menembak laser."""
        if not self.game_running:
            self.start_game()
        elif self.has_laser:
            self.shoot_laser()

    def shoot_laser(self):
        """Menembakkan peluru laser dari pesawat."""
        p_coords = self.paddle.get_position()
        if p_coords:
            l1 = Laser(self.canvas, p_coords[0] + 15, p_coords[1])
            l2 = Laser(self.canvas, p_coords[2] - 15, p_coords[1])
            self.lasers.extend([l1, l2])

    def add_score(self):
        """Menambahkan skor dan sistem combo multiplier."""
        self.score += 10 * self.combo
        self.combo = min(self.combo + 1, 5)
        if self.score > self.high_score:
            self.high_score = self.score
        self.update_hud()

    def update_hud(self):
        """Memperbarui teks informasi HUD di layar."""
        if self.hud_score:
            self.canvas.itemconfig(
                self.hud_score,
                text=f"Score:{self.score} (Hi:{self.high_score})",
            )
        if self.hud_lives:
            self.canvas.itemconfig(self.hud_lives, text=f"Shields:{self.lives}")
        if self.hud_combo:
            self.canvas.itemconfig(self.hud_combo, text=f"Combo:{self.combo}x")
        if self.hud_level:
            self.canvas.itemconfig(
                self.hud_level, text=f"Level:{self.level}/{self.max_levels}"
            )

    def clear_overlay_text(self):
        """Menghapus teks menu dan judul dari layar."""
        if self.overlay_text:
            self.canvas.delete(self.overlay_text)
            self.overlay_text = None
        if self.title_text:
            self.canvas.delete(self.title_text)
            self.title_text = None

    def setup_game(self):
        """Persiapan awal tampilan sebelum permainan dimulai."""
        self.clear_all_balls()
        self.clear_powerups()
        self.clear_lasers()
        self.clear_overlay_text()
        self.has_laser = False
        self.add_ball()

        if not self.hud_score:
            self.hud_score = self.canvas.create_text(
                90, 15, text=f"Score:0 (Hi:0)", fill="#00ffff", font=("Courier", 10, "bold")
            )
            self.hud_lives = self.canvas.create_text(
                240, 15, text=f"Shields:{self.lives}", fill="#00ffff", font=("Courier", 10, "bold")
            )
            self.hud_combo = self.canvas.create_text(
                370, 15, text=f"Combo:1x", fill="#00ffff", font=("Courier", 10, "bold")
            )
            self.hud_level = self.canvas.create_text(
                510, 15, text=f"Level:{self.level}/{self.max_levels}", fill="#00ffff", font=("Courier", 10, "bold")
            )
        else:
            self.update_hud()

        # Menampilkan teks judul animasi "Revan Mezzeluna"
        self.title_text = self.canvas.create_text(
            300,
            170,
            text="REVAN MEZZELUNA",
            fill="#00ffff",
            font=("Courier", 22, "bold"),
            justify="center",
        )

        self.overlay_text = self.canvas.create_text(
            300,
            230,
            text=f"LEVEL {self.level} - Press Space to Launch\n(Press 'R' to Restart)",
            fill="#ffffff",
            font=("Courier", 13, "bold"),
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
        """Membuat bola baru di atas pesawat dengan kecepatan santai."""
        paddle_coords = self.paddle.get_position()
        if paddle_coords:
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            ball_speed = 6 + (self.level - 1) * 1.5
            ball = Ball(self.canvas, x, 345, speed=ball_speed)
            self.balls.append(ball)
            self.paddle.set_ball(ball)
            self.items[ball.item] = ball

    def spawn_extra_ball(self, x, y):
        extra_ball = Ball(self.canvas, x, y, speed=6 + (self.level - 1) * 1.5)
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
        """Memulai permainan saat tombol Spasi ditekan."""
        self.clear_overlay_text()
        self.paddle.ball = None
        self.game_running = True
        self.game_loop()

    def next_level(self):
        """Melanjutkan ke level berikutnya."""
        self.level += 1
        self.game_running = False
        self.clear_all_balls()
        self.clear_powerups()
        self.clear_lasers()
        self.items.clear()
        self.canvas.delete("brick")

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.building_bricks_for_level()
        self.setup_game()

    def restart_game(self):
        """Mereset total permainan dari awal."""
        self.lives = 3
        self.score = 0
        self.combo = 1
        self.level = 1
        self.game_running = False
        self.canvas.delete("all")

        # Inisialisasi ulang bintang dan roket latar belakang
        self.stars = [BackgroundStar(self.canvas, self.width, self.height) for _ in range(60)]
        self.rocket = AnimatedRocket(self.canvas, self.width, self.height)

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
        self.hud_level = None
        self.overlay_text = None
        self.title_text = None

        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle

        self.building_bricks_for_level()
        self.setup_game()

    def defeat_boss(self):
        """Kondisi saat pemain berhasil mengalahkan Boss terakhir."""
        self.boss = None
        self.game_running = False
        self.clear_overlay_text()
        self.overlay_text = self.canvas.create_text(
            300,
            200,
            text="VICTORY!\nYOU DEFEATED THE FINAL BOSS!\nPress 'R' to Replay",
            fill="#f39c12",
            font=("Courier", 20, "bold"),
            justify="center",
        )

    def game_loop(self):
        """Loop utama permainan yang memperbarui posisi objek setiap frame."""
        if not self.game_running:
            return

        # Mengupdate animasi latar belakang (bintang & roket menyilang)
        for star in self.stars:
            star.update()
        self.rocket.update()

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
            if self.level < self.max_levels:
                self.next_level()
                return
            else:
                self.boss = Boss(self.canvas, self.width)

        if len(self.balls) == 0:
            self.lives -= 1
            self.update_hud()
            if self.lives < 0:
                self.game_running = False
                self.clear_overlay_text()
                self.overlay_text = self.canvas.create_text(
                    300,
                    200,
                    text="GAME OVER!\nPress 'R' to Retry",
                    fill="#ff3333",
                    font=("Courier", 24, "bold"),
                    justify="center",
                )
            else:
                self.game_running = False
                self.after(1000, self.setup_game)
        else:
            self.after(15, self.game_loop)

    def check_collisions(self):
        """Mendeteksi titik sentuh tabrakan antar objek."""
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
    root.title("Space Arcade - Revan Mezzeluna Ultimate Edition")
    game = Game(root)
    game.mainloop()