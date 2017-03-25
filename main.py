import pygame
from roche import Environment, Planet
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (1300, 700)
screen = pygame.display.set_mode((width, height))
pygame.display.set_icon(pygame.image.load('sigurdson_kris.png'))
pygame.display.set_caption('Gravity Test')

pygame.font.init()
font = pygame.font.SysFont('Sans', 60)

clock = pygame.time.Clock()

universe = Environment((width, height))
universe.colour = (0,0,0)

# Defines distance from the sides of the screen the orbit can be, in pixels.
hmargin = 25
vmargin = 25


# Input Coordinates for Moon's orbit
# Essentially the 'user input' for this simulation.
# Earth's radius is 6 371 000 m for reference.

# May transition to scientific notation in the future...

# The apoapsis (apogee in Earth-Moon system) is the highest point in an orbit, 
# input in metres from centre body's core. The Moon's apogee IRL is 4.054 * 10**8 m.
apoapsis = 1.00 * 10**8

# The periapsis (perigee in Earth-Moon system) is the lowest point in an orbit, 
# input in metres from centre body's core. The Moon's perigee IRL is 3.626 * 10**8 m.
periapsis = 1.00 * 10**7

# Because I have definitely input a smaller value for the apoapsis before.
if apoapsis < periapsis:
    apoapsis, periapsis = periapsis, apoapsis


# Pixel-to-Metre conversion.

# As we already defined the apoapsis, we'll use its height as our base 
# 'kilometre unit' by which we can convert to and from pixels to metres at will.


m = (apoapsis + periapsis)/(float(width - 2 * hmargin)) # in m / pixel


# I have the if statement there to check if the height of the window will be too
# small for the orbit. The program then adjusts the horizontal margin to fit
# properly 

if 2 * (apoapsis * periapsis)**0.5/m > height - 2 * vmargin:
    m = 2 * (apoapsis * periapsis)**0.5 / float(height - 2 * vmargin)
    hmargin = abs((width - (apoapsis + periapsis)/ m )/2)
    

# This G is in pixels
G = (6.674*10**-11)/m**3


earth_radius = 6371000 / m # in metres, converted to pixels through m
earth_mass = 5.972*10**24 # kg
earth = Planet((hmargin + (apoapsis / m), height/2), earth_radius, earth_mass)
earth.fixed = True
earth.colour = (100, 100, 255) # baby blue
universe.planets.append(earth)



moon_radius = 1737500 / m # in km, converted to pixels
moon_mass = 7.348*10**22 # kg
moon = Planet((hmargin, height/2), moon_radius, moon_mass)


# Based on the periapsis and apoapsis from earlier, this will provide the Moon
# with an initial velocity to make said orbit. We'll assume that the Moon's
# starting location is at the apoapsis, on the left side of the screen.

v = ((2 * m**3 * G * (earth_mass + moon_mass )) * \
    ((1 / apoapsis) - (1 / (periapsis + apoapsis))))**0.5

moon.velocity = Vector2D(0, - v/m) #m/s
moon.colour = (100, 100, 100)
universe.planets.append(moon)

# Time between simulation steps, increase to increase speed of moon
dt = 50

# Time scale
TIME_SCALE = 0.0001

# Keeps track of times the loop has run
i = 0

# Time between drawing the trail step in frames. Large values lead to geodesic-esque patterns!
timeStep = 10


running = True
while running:

    i += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    universe.update(G, dt)
    screen.fill(universe.colour)


    for p in universe.planets:

        # ~~~~~ Planet Trail Drawing Code ~~~~~ #

        # Placed prior to the planet drawing code to draw the trail underneath the planet.

        # Appends the trail list with the particle's current position.
        # For whatever reason, if these two ifs are compiled into one, everything breaks.
        # Hence the double if. 
        if i == timeStep:
            p.appendTrail(height)
        if i > timeStep:
            i = 0

        # If the trail has more than one point (necessary to actually make a line), draw the trail.
        if len(p.trail) > 1:
            pygame.draw.aalines(screen, p.line_colour, False, p.trail)

        # ~~~~~ End Planet Trail Drawing Code ~~~~~ #

        # I may have got text working
        if moon.areWeDead(earth) == True:
            screen.blit(font.render('YOU KILLED', True, (255,0,0), (255,255,255)), (100, 400))
            screen.blit(font.render('EVERYONE', True, (255,0,0), (255,255,255)), (110, 465))


        # Draws it so that (0,0) is the bottom left corner
        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.position.x), height - int(p.position.y), 2, 2))
        else:
            
            # Draws pretty anti-aliased outlines for each body.
            # There are two lines to make the outline a bit thicker.
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 1), 1)
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 0), 1)

            pygame.draw.circle(screen, p.colour, (int(p.position.x), height - int(p.position.y)), int(p.size), 0)


    pygame.display.flip()

    pygame.time.delay(int(TIME_SCALE * dt * 1000))

pygame.quit()  # IDLE interpreter friendly
