import pygame, random
import sys
import data.code.map_load as MAPLOAD

# Pygame 초기화
pygame.mixer.init()
pygame.init()
class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.life = 100

    def update(self):
        self.rect.x += self.velocity[0] * 5
        self.rect.y += self.velocity[1] * 5
        self.life -= 1
        if self.life <= 0:
            self.kill()

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

# 리듬 게임 메인 클래스
class Game:
    def __init__(self):
        # 화면 설정
        self.screen = pygame.display.set_mode((640, 480))
        # clock 설정
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False
        self.effect1 = pygame.mixer.Sound("data\\sound\\effect1.wav")
        self.effect2 = pygame.mixer.Sound("data\\sound\\effect2.wav")
        self.effect3 = pygame.mixer.Sound("data\\sound\\effect3.wav")
        self.effect4 = pygame.mixer.Sound("data\\sound\\Tack!.mp3")
        # 결과 이미지 로드
        self.perfect_image = pygame.image.load("data/images/perfect.png")
        self.result_image = None
        self.result_image_pos = (320, 240)
        self.chabo_bg_rects_white = [
            pygame.rect.Rect(0, 460, 50, 20),
            pygame.rect.Rect(75, 460, 50, 20),
            pygame.rect.Rect(150, 460, 50, 20),
            pygame.rect.Rect(225, 460, 50, 20),
        ]
        self.chabo_rate = [[], [], [], []]

    def summon_chabo(self, type):
        rect_sprite = Chabo(type + 1)
        all_sprites.add(rect_sprite)
        rect_sprite.GetDown()
        self.chabo_rate[type].append("CHABO")

    def check_collision(self, type):
        for sprite in all_sprites:
            if sprite.rect.colliderect(self.chabo_bg_rects_white[type]):
                accuracy = 460 - sprite.rect.y
                for _ in range(20):
                    particle = Particle(sprite.rect.center)
                    particles.add(particle)
                    all_sprites.add(particle)
                if -5 <= accuracy <= 5:
                    self.result_image = self.perfect_image

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
        k = 0
        all_sprites.update()
        all_sprites.draw(self.screen)
        for rec in self.chabo_bg_rects_white:
            k += 1
            pygame.draw.rect(self.screen, (255, 255, 255), rec)
        if self.result_image:
            self.screen.blit(self.result_image, self.result_image_pos)

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
