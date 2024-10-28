import json
import os
from pathlib import Path

# 2024-08-25 오후 2:47 기준 밑에 있는 코드가 ModuleNotFoundError 떴는데 ㅅㅂ 왜뜨는건데 (qwru0905)
# 고침. 아니 왜 cmd 로 한게 인식이 왜 안되는건데 (qwru0905)
import pygame
import sys
import data.code.map_load as MAPLOAD
import math, random
import time

# 460일 때 perfect임

# Pygame 초기화
pygame.mixer.init()
pygame.init()

# clock 설정
clock = pygame.time.Clock()

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
        self.type = type
        # 눌러야 하는 시간
        # (타이밍 수정)
        self.note_time = time.time() * 1000 + (460 / speed) * 1000
        #print(pygame.time.get_ticks())
        #print((460 / speed)*1000)
        #print(self.note_time)

    def GetDown(self):
        self.moving_down = True

    def update(self):
        if self.note_time - time.time() * 1000 <= -50:
            self.kill()
        if self.moving_down:
            self.rect.y = 460 - (self.speed * (self.note_time / 1000 - time.time()))  # 스프라이트 y좌표 위치 수정

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
        self.image.set_alpha(self.life * 2)
        if self.life <= 0:
            self.kill()


class Button:
    def __init__(self, x, y, width, height, color, text='', img=''):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.img = img

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

        # 버튼에 이미지가 있을 경우 이미지 그리기
        if self.img != '':
            img = pygame.image.load(current_dir / self.img)
            screen.blit(img, (
                self.x + (self.width / 2 - img.get_width() / 2),
                self.y + (self.height / 2 - img.get_height() / 2)
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

        # perfect +-33.33ms(2프레임), ok +-50.00ms(3프레임)
        #self.perfect_judge = 33.33
        #self.ok_judge = 50.00
        # 지금 음악이 없어서 타이밍 잡기 디지게 힘드니까 좀 여유롭게 할게
        # perfect +-50.00ms(3프레임), ok +-100.00ms(6프레임)
        self.perfect_judge = 50.00
        self.ok_judge = 100.00

        self.perfect_count = 0
        self.ok_count = 0

        self.chabo_count = 0

        self.now_screen = 0

        self.now_page = 1
        self.max_page = 1

    def summon_chabo(self, type, speed):
        rect_sprite = Chabo(type + 1, speed)
        # noinspection PyTypeChecker
        all_sprites.add(rect_sprite)
        rect_sprite.GetDown()
        self.chabo_rate[type].append("CHABO")

    def check_collision(self, type):
        for sprite in all_sprites:
            """
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
            """
            if sprite.type - 1 != type:
                continue

            accuracy = sprite.note_time - time.time() * 1000
            #print(sprite.note_time)
            #print(time.time() * 1000)
            #print(accuracy)
            if -self.ok_judge <= accuracy <= self.ok_judge:
                sprite.kill()
                for _ in range(40):
                    particle = Particle(sprite.rect.center)
                    particles.add(particle)
                if -self.perfect_judge <= accuracy <= self.perfect_judge:
                    self.result_image = self.perfect_image
                    self.perfect_count += 1
                else:
                    self.result_image = self.ok_image
                    self.ok_count += 1

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
            self.screen.blit(self.chabo_collide_sp, (75 * i, 460))

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
                             (
                                 self.result_image_pos[0] - width // 2 + 200,
                                 self.result_image_pos[1] - height // 2 + 100))

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
                        self.now_screen = 1
                        return

    song_file_name = ""

    def song_select(self):
        self.screen.fill((0, 0, 0))
        file_list = os.listdir(current_dir / "data/map")
        file_list = [file for file in file_list if file.endswith('.json')]
        print(file_list)
        song_name_list = []
        for file_name in file_list:
            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                song_name_list.append(json.load(file)["map_name"])

        self.max_page = math.ceil(len(song_name_list) / 3)
        print(song_name_list)
        # self.screen = pygame.display.set_mode((640, 480)) (확인용)
        button1 = Button(300, 75, 300, 75, (255, 255, 255), '[song1]')
        button2 = Button(300, 175, 300, 75, (255, 255, 255), '[song2]')
        button3 = Button(300, 275, 300, 75, (255, 255, 255), '[song3]')
        right_button = Button(500, 400, 60, 60, (255, 255, 255), '', 'data/images/rightButtonBasic.png')
        left_button = Button(70, 400, 60, 60, (255, 255, 255), '', 'data/images/leftButtonBasic.png')
        right_button.draw(self.screen)
        left_button.draw(self.screen)
        for i in range(3):
            i1 = i + (self.now_page - 1) * 3
            if i1 < len(song_name_list):
                print(f"{i + 1}. {song_name_list[i1]}")
                if i1 % 3 == 0:
                    button1.text = song_name_list[i1]
                    button1.draw(self.screen, (0, 0, 0))
                if i1 % 3 == 1:
                    button2.text = song_name_list[i1]
                    button2.draw(self.screen, (0, 0, 0))
                if i1 % 3 == 2:
                    button3.text = song_name_list[i1]
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
                                    self.now_screen = 2
                                    break
                        return
                    elif button2.is_over(pygame.mouse.get_pos()):
                        print("Button2 clicked!")
                        for file_name in file_list:
                            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                                if button2.text == json.load(file)["map_name"]:
                                    self.song_file_name = file_name
                                    self.now_screen = 2
                                    break
                        return
                    elif button3.is_over(pygame.mouse.get_pos()):
                        print("Button3 clicked!")
                        for file_name in file_list:
                            with open(current_dir / "data/map" / file_name, "r", encoding="utf-8") as file:
                                if button3.text == json.load(file)["map_name"]:
                                    self.song_file_name = file_name
                                    self.now_screen = 2
                                    break
                        return
                    elif left_button.is_over(pygame.mouse.get_pos()):
                        if self.now_page == 1:
                            self.now_page = self.max_page
                        else:
                            self.now_page -= 1
                        return
                    elif right_button.is_over(pygame.mouse.get_pos()):
                        if self.now_page == self.max_page:
                            self.now_page = 1
                        else:
                            self.now_page += 1
                        return

    def game_start(self):
        m = MAPLOAD.Chabo_map_load(current_dir / "data/map" / self.song_file_name)
        m_data = m.load()
        if not m_data:  # JSON 데이터가 없는 경우 종료
            print("데이터를 불러오지 못했습니다.")
            # 화면 그거 다시 만들어야 할 것 같은
            return

        chabo_list = m_data["chabo"]
        for _ in chabo_list:
            for __ in chabo_list[_]:
                self.chabo_count += 1
        print(self.chabo_count)

        timer = 0
        shown_chabo_count = 0
        is_game_end = False
        while True:
            timer += 1
            if "version" not in m_data:
                for i in chabo_list:
                    if str(timer) == str(i):
                        for k in chabo_list[i]:
                            self.summon_chabo(k - 1, 2.5 * 60)
                            shown_chabo_count += 1
            elif m_data["version"] == 0.1:
                for i in chabo_list:
                    if str(timer) == str(i):
                        for k in chabo_list[i]:
                            self.summon_chabo(k - 1, m_data["note_speed"])
                            shown_chabo_count += 1

            if shown_chabo_count >= self.chabo_count:
                is_game_end = True
            self.draw()
            self.event()
            pygame.display.update()
            self.screen.fill(0)
            self.clock.tick(60)
            if is_game_end and len(all_sprites) == 0:
                # 끝남이 너무 도배되긴 하는데, 뭐 어떻게든 되겠지
                # 나 참고로 여기 주석 할 때 실수로 // 이렇게 함
                print("끝남")
                self.now_screen = 3
                return

    def run(self):
        self.start_menu()
        while True:
            if self.now_screen == 1:
                self.song_select()
            elif self.now_screen == 2:
                self.game_start()
            elif self.now_screen == 3:
                self.result()
                self.reset()

    def result(self):
        # 점수는 1,000,000 (백만점) 최대
        # perfect는 1000000/체보의 개수
        # ok는 500000/체보의 개수
        print("perfect: " + str(self.perfect_count))
        print("ok: " + str(self.ok_count))

        score = ((1000000 / self.chabo_count) * self.perfect_count
                 + (500000 / self.chabo_count) * self.ok_count)
        formatted_number = format(score, ",.0f")
        print(formatted_number)  # 출력: 123,456

        font = pygame.font.Font(None, 50)
        score_text = font.render(formatted_number, 1, (255, 255, 255))
        perfect_count_text = font.render("PERFECT: " + str(self.perfect_count), 1, (255, 255, 255))
        ok_count_text = font.render("OK: " + str(self.ok_count), 1, (255, 255, 255))
        self.screen.blit(score_text, (50, 100))
        self.screen.blit(perfect_count_text, (50, 175))
        self.screen.blit(ok_count_text, (50, 250))
        button = Button(120, 375, 400, 75, (255, 255, 0), 'BACK')
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

    def reset(self):
        self.perfect_count = 0
        self.ok_count = 0
        self.chabo_count = 0
        self.now_screen = 1


G = Game()
G.run()
