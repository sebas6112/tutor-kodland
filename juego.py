import pygame, random, sys

SCREEN_WIDTH = 1200     #Tamaño de la ventana
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])     #Creación de la ventana y asignación del nombre
pygame.display.set_caption("Aventura en paint!!!")

CANVAS_X1 = 35          #Tamaño del espacio de juego "lienzo de paint"
CANVAS_Y1 = 208
CANVAS_X2 = 1159
CANVAS_Y2 = 681

STAR_WIDTH = 40         #Tamaño de la estrella 
STAR_HEIGHT = 30

steps = 5               #Variables como velocidades de movimiento e inicializadores
jump_speed = 10
score = 0
game_over = True

BLACK = (  0,   0,  0)  #Colores usados en R,G,B
RED = ( 255, 0, 0)
GRAY = ( 200, 200, 200)

def draw_text(surface, text, size, x, y, c):
    """Función para dibujar texto (text) 
    de un tamaño (size) en una superficie (surface)
    en una posición (x, y) y de un color (c)"""
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, c)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

class Star(pygame.sprite.Sprite):
    """Sprite estrella, es la forma de conseguir puntos"""
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("star.png").convert()
        self.image = pygame.transform.scale(self.image,(STAR_WIDTH, STAR_HEIGHT))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

class BoxSprite( pygame.sprite.Sprite ):
    """Sprite de las cajas que actúan como plataformas del juego
    dibujadas por el usuario"""
    def __init__( self, drag_rect ):
        super().__init__()
        self.image = pygame.Surface( ( drag_rect.width, drag_rect.height ) )
        self.rect  = drag_rect.copy()
        self.image.fill( GRAY )


class Player(pygame.sprite.Sprite):
    """Sprite del jugador con todas sus funciones e interacciones"""
    def __init__(self):
        super().__init__()
        self.movex = 0
        self.movey = 0
        self.jumping = False
        self.inplatform = False
        self.frame = 0
        self.images = []
        #Importación de todas las imágenes de animación del jugador
        #Además definición de cada una de sus características
        for i in range(1,11):
            img = pygame.image.load(f"stickman\sm_{i}.png").convert()
            img = pygame.transform.scale_by(img,0.1)
            img.set_colorkey(BLACK)
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.width = self.image.get_width()
            self.height = self.image.get_height()
    def control(self, x, y):
        """Función para mover el jugador"""
        if x == 0 and y == 0:
            self.movex = 0
            self.movey = 0
        else:
            self.movex += x
            self.movey += y
        if y > 0:
            self.jumping = True
    
    def update(self, boxes):
        """Función que permite actualizar tanto las 
        animaciones como las posiciones del jugador"""

        # Revisión de que el jugador no se salga del área de juego
        if self.rect.x < CANVAS_X1:
            self.rect.x = CANVAS_X1
        elif self.rect.x > CANVAS_X2 - self.image.get_width():
            self.rect.x = CANVAS_X2 - self.image.get_width()
        else:
            self.rect.x = self.rect.x + self.movex
        # Revisión de colisiones con bloques
        lista_impactos_bloques = pygame.sprite.spritecollide(self, boxes, False)
        for bloque in lista_impactos_bloques:
            # Colisiones horizontales
            if self.movex > 0:
                self.rect.right = bloque.rect.left
            elif self.movex < 0:
                self.rect.left = bloque.rect.right
        
        if self.rect.y < CANVAS_Y1:
            self.rect.y = CANVAS_Y1
            self.jumping = True
        elif self.rect.y > CANVAS_Y2 - self.image.get_height():
            self.rect.y = CANVAS_Y2 - self.image.get_height()
            self.movey = 0
            self.jumping = False
        else:
            self.rect.y = self.rect.y - self.movey
            if self.jumping == True:
                self.movey -= 1

        # Colisiones verticales
        lista_impactos_bloques = pygame.sprite.spritecollide(self, boxes, False) 
        for bloque in lista_impactos_bloques:
            if self.rect.bottom < bloque.rect.bottom:
                self.rect.bottom = bloque.rect.top
                self.jumping = False
                self.inplatform = True
                self.movey = 0
                self.actual_platform = bloque
            elif self.rect.top < bloque.rect.bottom:
                self.rect.top = bloque.rect.bottom
        if self.inplatform:
            if (self.actual_platform.rect.left > self.rect.right) or (self.actual_platform.rect.right < self.rect.left):
                self.control(0, jump_speed)
                self.inplatform = False
                self.jumping = True
            
        # Quieto
        if self.movex == 0 and self.movey == 0:
             self.image = self.images[0]

        # caminar hacia la izquierda
        if self.movex < 0:
            self.frame += 1
            if self.frame > 7:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame], True, False)

        # caminar hacia la derecha
        if self.movex > 0:
            self.frame += 1
            if self.frame > 7:
                self.frame = 0
            self.image = self.images[self.frame]

            

class Game(object):
    """Clase del juego donde se crean todos los sprites
    se analizan todos los eventos y ocurre la lógica del juego"""
    def __init__(self):

        self.star_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        
        self.star = Star()
        self.star.rect.x = random.randrange(CANVAS_X1 + (STAR_WIDTH/2), CANVAS_X2 - (STAR_WIDTH/2))
        self.star.rect.y = random.randrange(CANVAS_Y1 + (STAR_HEIGHT/2), CANVAS_Y2 - 150)
        self.star_list.add(self.star)
        self.all_sprites_list.add(self.star)

        self.player = Player()
        self.player.rect.x = CANVAS_X1 + 2
        self.player.rect.y = CANVAS_Y2 - self.player.height - 2
        self.all_sprites_list.add(self.player)

        self.user_boxes_group = pygame.sprite.Group()    # initially empty

        self.rect_start = ( -1, -1 ) # start position of drawn rectangle
        self.drag_start = ( -1, -1 ) # start position of a mouse-drag

    def process_events(self):
        global game_over
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    game_over = False
                    self.__init__()
                    
            if event.type == pygame.KEYDOWN:
                if event.key == ord('q'):
                    pygame.quit()
                    try:
                        sys.exit()
                    finally:
                        main = False
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    self.player.control(-steps,0)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    self.player.control(steps, 0)
                if event.key == pygame.K_UP or event.key == ord('w'):
                    self.player.control(0,jump_speed)
                if event.key == ord('r'):
                    self.__init__()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    self.player.control(0, 0)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    self.player.control(0, 0)
                if event.key == pygame.K_UP or event.key == ord('w'):
                    self.player.control(0,0)

            if (event.type == pygame.MOUSEBUTTONDOWN):
                self.rect_start = pygame.mouse.get_pos()

            elif ( event.type == pygame.MOUSEBUTTONUP ):            

                if ( self.rect_start != ( -1, -1 ) ):
                    if ( self.rect_start > self.mouse_pos ):
                        swapper = ( self.mouse_pos[0], self.mouse_pos[1] )
                        self.mouse_pos = self.rect_start
                        self.rect_start = swapper

                    new_width  = abs( self.mouse_pos[0] - self.rect_start[0] )
                    new_height = abs( self.mouse_pos[1] - self.rect_start[1] )

                    if ( new_width > 0 and new_height > 0 ):
                        new_sprite = BoxSprite( pygame.Rect( self.rect_start, ( new_width, new_height ) ) )
                        self.all_sprites_list.add( new_sprite )
                        self.user_boxes_group.add(new_sprite)
                    self.rect_start = ( -1, -1 )
        return False
    
    def run_logic(self):
        global score
        global game_over
        if not game_over:
            self.all_sprites_list.update(self.user_boxes_group)

            meteor_hit_list = pygame.sprite.spritecollide(self.player, self.star_list, True)

            for star in meteor_hit_list:
                score += 1
            if len(self.star_list) == 0:
                game_over = True
        self.player.update(self.user_boxes_group)
        

    def display_frame(self, screen):
        background = pygame.image.load("paint_background.png").convert()
        background = pygame.transform.scale(background,(SCREEN_WIDTH,SCREEN_HEIGHT))
        screen.blit(background, [0,0])
        if ( self.rect_start != ( -1, -1 ) ):
        # Use a lines instead of a Rect, so we don't have to handle width/height co-ordinate position issues 
            box = [ self.rect_start, (self.mouse_pos[0], self.rect_start[1] ), self.mouse_pos, ( self.rect_start[0], self.mouse_pos[1] ) ]
            pygame.draw.lines(screen, BLACK, True, box, 1 )
        draw_text(screen, "Puntaje: " + str(score), 40, 100, 170, RED)
        if game_over:
            draw_text(screen, "¡¡AVENTURAS EN PAINT!!", 65, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, BLACK)
            draw_text(screen, "Para jugar sigue las siguientes instrucciones:", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 11/25, BLACK)
            draw_text(screen, "1) Te puedes mover con las flechas del teclado o con A W D", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT  * 12/25, BLACK)
            draw_text(screen, "2) Construye tu mundo para escalar haciendo click y arrastrando el mouse", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 13/25, BLACK)
            draw_text(screen, "3) Consigue estrellas para ganar más puntos", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT* 14/25, BLACK)
            draw_text(screen, "4) Para reiniciar el nivel presiona R", 20, SCREEN_WIDTH // 2,SCREEN_HEIGHT  * 15/25, BLACK)
            draw_text(screen, "5) Para salir del juego presiona Q", 20, SCREEN_WIDTH // 2,SCREEN_HEIGHT  * 16/25, BLACK)
            draw_text(screen, "Da click para continuar", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 21/25, BLACK)

        if not game_over:
            self.all_sprites_list.draw(screen)

        pygame.display.flip()

def main():
    pygame.init()
    done = False
    clock = pygame.time.Clock()

    game = Game()

    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()