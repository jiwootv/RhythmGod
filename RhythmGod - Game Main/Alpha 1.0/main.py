import json
import os
from pathlib import Path

# 2024-08-25 오후 2:47 기준 밑에 있는 코드가 ModuleNotFoundError 떴는데 ㅅㅂ 왜뜨는건데 (qwru0905)
# 고침. 아니 왜 cmd 로 한게 인식이 왜 안되는건데 (qwru0905)
import pygame
import sys
import data.code.map_load as MAPLOAD
import math, random

# Pygame 초기화
pygame.mixer.init()
pygame.init()

current_dir = Path(__file__).resolve().parent

# 채보 스프라이트 코드
class Chabo(pygame.sprite.Sprite):
    def __init__(self, type, speed):
        super().__init__()
        self.image = pygame.Surface((50, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (75 * (type - 1), 0)
        self.moving_down = False
        self.speed = speed

    def GetDown(self):
        self.moving_down = True

    def update(self):
        if self.rect.top > 470:
            self.kill()
        if self.moving_down:
            self.rect.y += self.speed  # 스프라이트가 내려가는 속도 조절

    def get(self):
        return self.rect

# 스프라이트 그룹 생성
all_sprites = pygame.sprite.Group()
particles = pygame.sprite.Group()

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.life = 40

    def update(self):
        self.rect.x += self.velocity[0] * 1
        self.rect.y += self.velocity[1] * 5
        self.life -= 1
        self.image.set_alpha(self.life*2)
        if self.life <= 0:
            self.kill()

class Button:
    def __init__(self, x, y, width, height, color, text=''):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text

    def draw(self, screen, outline=None):
        # 버튼에 외곽선이 있을 경우 그리기
        if outline:
            pygame.draw.rect(screen, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        # 버튼 그리기
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)

        # 버튼에 텍스트가 있을 경우 텍스트 그리기
        if self.text != '':
            font = pygame.font.Font(None, 30)
            text = font.render(self.text, 1, (0, 0, 0))
            screen.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2)
            ))

    def is_over(self, pos):
        # pos는 마우스의 (x, y) 좌표
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False

# 리듬 게임 메인 클래스
class Game:
    def __init__(self):
        # 화면 설정
        self.screen = pygame.display.set_mode((640, 480))
        # clock 설정
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False

        # 결과 이미지 로드
        self.perfect_image = pygame.image.load(current_dir / "data/images/perfect.png").convert_alpha()
        self.perfect_image = pygame.transform.scale(self.perfect_image, (148, 49))
        self.ok_image = pygame.image.load(current_dir / "data/images/Ok.png")

        self.result_image = None
        self.result_alpha = 0
        self.result_image_pos = (320, 240)
        self.result_display_time = 0
        self.fade_out_time = 500  # 페이드 아웃 시간 (밀리초)
        self.chabo_bg_rects_white = [
            pygame.rect.Rect(0, 460, 50, 20),
            pygame.rect.Rect(75, 460, 50, 20),
            pygame.rect.Rect(150, 460, 50, 20),
            pygame.rect.Rect(225, 460, 50, 20),
        ]

        self.chabo_rate = [[], [], [], []]
        self.chabo_collide_sp = pygame.image.load(current_dir / "data/images/chabo_collide_rect.png")
        pygame.display.set_caption("RhythmGod")

    def summon_chabo(self, type, speed):
        rect_sprite = Chabo(type + 1, speed)
        # noinspection PyTypeChecker
        all_sprites.add(rect_sprite)
        rect_sprite.GetDown()
        self.chabo_rate[type].append("CHABO")

    def check_collision(self, type):
        for sprite in all_sprites:
            if sprite.rect.colliderect(self.chabo_bg_rects_white[type]):
                accuracy = 460 - sprite.rect.y
                print(len(all_sprites))
                sprite.kill()
                print(len(all_sprites))
                for _ in range(40):
                    particle = Particle(sprite.rect.center)
                    particles.add(particle)
                if accuracy <= 5:
                    self.result_image = self.perfect_image
                else:
                    self.result_image = self.ok_image

                self.result_alpha = 0
                self.result_display_time = pygame.time.get_ticks()

                return True
        return False

    def event(self):
        # 키입력 등 이벤트 감지
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((640, 480))
                    print(self.is_fullscreen)
                if event.key == pygame.K_a:  # 'a' 키를 누르면 첫 번째 채보 라인을 체크
                    c = self.check_collision(0)

                if event.key == pygame.K_s:  # 's' 키를 누르면 두 번째 채보 라인을 체크
                    c = self.check_collision(1)

                if event.key == pygame.K_k:  # 'k' 키를 누르면 세 번째 채보 라인을 체크
                    c = self.check_collision(2)

                if event.key == pygame.K_l:  # 'l' 키를 누르면 네 번째 채보 라인을 체크
                    c = self.check_collision(3)


    def draw(self):
        global scale_factor
        k = 0
        all_sprites.update()
        all_sprites.draw(self.screen)
        particles.update()
        particles.draw(self.screen)
        # for rec in self.chabo_bg_rects_white:
        #     k += 1
        #     pygame.draw.rect(self.screen, (255, 255, 255), rec)
        for i in range(4):
            self.screen.blit(self.chabo_collide_sp, (75*i, 460))

        if self.result_image:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.result_display_time
            if elapsed_time < 500:
                # 로그 함수를 이용한 부드러운 등장 (크기 조절)
                scale_factor = min(2.0, math.log10(1 + elapsed_time / 100))
                self.result_alpha = min(255, int(255 * math.log10(1 + elapsed_time / 100)))
            else:
                # 페이드 아웃
                fade_elapsed = elapsed_time - 1000
                self.result_alpha = max(0, 255 - int(255 * (fade_elapsed / self.fade_out_time)))
                if self.result_alpha == 0:
                    self.result_image = None  # 이미지 숨기기
                scale_factor = 1.0  # 페이드 아웃 중 크기 조절 없음

        if self.result_image:
            width = int(self.result_image.get_width() * scale_factor)
            height = int(self.result_image.get_height() * scale_factor)
            image_copy = pygame.transform.scale(self.result_image, (width, height))
            image_copy.set_alpha(self.result_alpha)
            self.screen.blit(image_copy,
                             (self.result_image_pos[0] - width // 2+200, self.result_image_pos[1] - height // 2+100))

    def start_menu(self):
        button = Button(120, 375, 400, 75, (0, 255, 0), 'START')
        button.draw(self.screen, (0, 0, 0))

        while True:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.is_over(pygame.mouse.get_pos()):
                        print("Button clicked!")
                        return

    song_file_name = ""
    def song_select(self):
        self.screen.fill((0, 0, 0))
        file_list = os.listdir(current_dir / "data/map")
        file_list = [file for file in file_list if file.endswith('.json') or file.endswith('.rgsf')]   # .rgsf는 rhythm god song file의 줄인 말임. zip 파일 형식으로 파일을 저장할 예정
        print(file_list)
        song_name_list = []
        for file_name in file_list:
            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                song_name_list.append(json.load(file)["map_name"])

        print(song_name_list)
        # self.screen = pygame.display.set_mode((640, 480)) (확인용)
        button1 = Button(300, 100, 300, 75, (255, 255, 255), '[song1]')
        button2 = Button(300, 200, 300, 75, (255, 255, 255), '[song2]')
        button3 = Button(300, 300, 300, 75, (255, 255, 255), '[song3]')
        for i in range(3):
            if i < len(song_name_list):
                print(f"{i + 1}. {song_name_list[i]}")
                if i % 3 == 0:
                    button1.text = song_name_list[i]
                    button1.draw(self.screen, (0, 0, 0))
                if i % 3 == 1:
                    button2.text = song_name_list[i]
                    button2.draw(self.screen, (0, 0, 0))
                if i % 3 == 2:
                    button3.text = song_name_list[i]
                    button3.draw(self.screen, (0, 0, 0))
        while True:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button1.is_over(pygame.mouse.get_pos()):
                        print("Button1 clicked!")
                        for file_name in file_list:
                            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                                if button1.text == json.load(file)["map_name"]:
                                    self.song_file_name = file_name
                                    break
                        return
                    elif button2.is_over(pygame.mouse.get_pos()):
                        print("Button2 clicked!")
                        for file_name in file_list:
                            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                                if button2.text == json.load(file)["map_name"]:
                                    self.song_file_name = file_name
                                    break
                        return
                    elif button3.is_over(pygame.mouse.get_pos()):
                        print("Button3 clicked!")
                        for file_name in file_list:
                            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                                if button3.text == json.load(file)["map_name"]:
                                    self.song_file_name = file_name
                                    break
                        return


    def game_start(self):
        m = MAPLOAD.Chabo_map_load(current_dir / "data/map" / self.song_file_name)
        m_data = m.load()
        if not m_data:  # JSON 데이터가 없는 경우 종료
            print("데이터를 불러오지 못했습니다.")
            pygame.quit()
            sys.exit()

        timer = 0
        while True:
            timer += 1
            if not "version" in m_data:
                for i in m_data["chabo"]:
                    if str(timer) == str(i):
                        for k in m_data["chabo"][i]:
                            self.summon_chabo(k - 1, 2.5)
            elif m_data["version"] == 0.1:
                for i in m_data["chabo"]:
                    if str(timer) == str(i):
                        for k in m_data["chabo"][i]:
                            self.summon_chabo(k - 1, m_data["note_speed"])

            self.draw()
            self.event()
            pygame.display.update()
            self.screen.fill(0)
            self.clock.tick(60)
            if len(all_sprites) == 0:
                # 끝남이 너무 도배되긴 하는데, 뭐 어떻게든 되겠지
                print("끝남")

    def run(self):
        self.start_menu()
        self.song_select()
        self.game_start()

G = Game()
G.run()
