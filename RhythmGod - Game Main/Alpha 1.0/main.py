import pygame
import sys
import data.code.map_load as MAPLOAD
import math, random

# Pygame 초기화
pygame.mixer.init()
pygame.init()

# 채보 스프라이트 코드
class Chabo(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.image = pygame.Surface((50, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (75 * (type - 1), 0)
        self.moving_down = False

    def GetDown(self):
        self.moving_down = True

    def update(self):
        if self.rect.top > 470:
            self.kill()
        if self.moving_down:
            self.rect.y += 2.5  # 스프라이트가 내려가는 속도 조절

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

# 리듬 게임 메인 클래스
class Game:
    def __init__(self):
        # 화면 설정
        self.screen = pygame.display.set_mode((640, 480))
        # clock 설정
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False

        # 결과 이미지 로드
        self.perfect_image = pygame.image.load("data/images/perfect.png").convert_alpha()
        self.perfect_image = pygame.transform.scale(self.perfect_image, (148, 49))
        self.ok_image = pygame.image.load("data/images/Ok.png")

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
        self.chabo_collide_sp = pygame.image.load("data\\images\\chabo_collide_rect.png")

    def summon_chabo(self, type):
        rect_sprite = Chabo(type + 1)
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

    def run(self):
        self.summon_chabo(3)
        m = MAPLOAD.Chabo_map_load("data\\map\\animals")
        m_data = m.load()
        if not m_data:  # JSON 데이터가 없는 경우 종료
            print("데이터를 불러오지 못했습니다.")
            pygame.quit()
            sys.exit()

        timer = 0
        while True:
            timer += 1
            for i in m_data["chabo"]:
                if str(timer) == str(i):
                    for k in m_data["chabo"][i]:
                        self.summon_chabo(k - 1)

            self.draw()
            self.event()
            pygame.display.update()
            self.screen.fill((0))
            self.clock.tick(60)

G = Game()
G.run()
