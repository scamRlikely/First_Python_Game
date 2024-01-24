#!/usr/bin/env python



"""
                                        IMPORTANT REMINDER
    FOR LOADING NEW SCREENS, JUST RESET THE VALUES OF EVERYTHING, DON'T FORGET TO WIPE OLD OBJECTS
    idea: maybe make an old list to store the last room you were in (like for the attacks or sum)

"""

# Author: Shao Zhang, Phil Saltzman, and Greg Lindley
# Last Updated: 2015-03-13
#
# This tutorial demonstrates the use of tasks. A task is a function that
# gets called once every frame. They are good for things that need to be
# updated very often. In the case of asteroids, we use tasks to update
# the positions of all the objects, and to check if the bullets or the
# ship have hit the asteroids.
#
# Note: This definitely a complicated example. Tasks are the cores of
# most games so it seemed appropriate to show what a full game in Panda
# could look like.
import math
from direct.gui import *
from panda3d.egg import *
from direct.actor.Actor import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, TransparencyAttrib
from panda3d.core import LPoint3, LVector3
from panda3d.core import SamplerState
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from math import sin, cos, pi
from random import randint, choice, random
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
import sys
# Constants that will control the behavior of the game. It is good to
# group constants like this so that they can be changed once without
# having to find everywhere they are used in code

# And I still have to find all the individual methods in the library

#  WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP
#  WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP
#  WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP

#Patch notes: added schizophrenia
PL_INV = {
    "gun" : "WHAT THE FUCK IS A KILOMETERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH", #Magazine comes separate, but it gives you plus 10 intimidation
    "stick" : "Has the remains of what I hope is smores on the end", #Splinter ability, only happens on crit, causes mild annoyance
    "spiked boots" : "Always found near platform shoes and hair dye", #Gives the slow down effect in combat
    "fashionable scarf" : "Hey, watch the ascot", #Make you cute, which makes sparing people easier??
    "sharpened stick" : "The best sword a small child could ask for", #Just a better version of the stick #Maybe it's craftable when you find a stick and talk to someone?
    "laser pointer" : "Hope your opponent is a cat or doesn't wear blue light glasses", #If someone shines it 10 times in a row it signals a nuke on the enemy
    "gun magazine" : "Empty :(", #Projectile weapon, does double damage on melee but melee is only in the action menu heehee
    "pencil" : "The tip breaks after the first hit", #Add sharpen as an action, maxes out at 3 sharpens, does extra damage for each sharpen
    "king rat" : "a very royal rat", #A cool little plush or pet idk
    "Rat King" : "Don't look this up", #A disgusting abomination based off of a real world rat king
    "bouncy boots" : "boioioioing", #Maybe a dash forward/overworld jump ability?
    "crock socks" : "crocodile mouths you CAN put your feet in", #Very cool socks :)
    "cheese" : "attracts mice" #Makes rat encounters more likely
} #Not explaining this until it works cuz idk if i'm using it yet
HEALTH = 10
HEALTH_REF = 10
SPRITE_POS = 55     # Essentially just zoom in or out, but only the default value, 55, will work without tweaking everything else
# dimensions is 40x30 units
#The units suck so much because it doesn't tell you the exact pixel ratio, but rather a ratio based on how big a minimized window is per moniter.
SCREEN_X = 20       # Screen goes from -20 to 20 on X
#Sets positive (and negative) max for x
#real x and y are double the int input
SCREEN_Y = 15       # Screen goes from -15 to 15 on Y
TURN_RATE = 180     # Degrees ship can turn in 1 second
ACCELERATION = 10   # Ship acceleration in units/sec/sec
MAX_VEL = 6         # Maximum ship velocity in units/sec
MAX_VEL_SQ = MAX_VEL ** 2  # Square of the ship velocity
DEG_TO_RAD = pi / 180  # translates degrees to radians for sin and cos
BULLET_LIFE = 2     # How long bullets stay on screen before removed
BULLET_REPEAT = .2  # How often bullets can be fired
BULLET_SPEED = 10   # Speed bullets move
AST_INIT_VEL = 1    # Velocity of the largest asteroids
AST_INIT_SCALE = 2.75  # Initial asteroid scale
AST_VEL_SCALE = 2.2  # How much asteroid speed multiplies when broken up
AST_SIZE_SCALE = .6  # How much asteroid scale changes when broken up
AST_MIN_SCALE = 1.1  # If and asteroid is smaller than this and is hit,
# it disapears instead of splitting up




def inventoryAppend():
    g


# This helps reduce the amount of code used by loading objects, since all of
# the objects are pretty much the same.
def loadObject(tex=None, pos=LPoint3(0, 0), depth=SPRITE_POS, scale=1,
               transparency=True, velocity=0):
    #DO NOT MESS WITH THE TRANSPARENCY IT MESHES ALL LAYERS INTO ONE AND NOTHING SHOWS UP
    # Every object uses the plane model and is parented to the camera
    # so that it faces the screen.
    obj = loader.loadModel("models/plane")
    obj.reparentTo(camera)

    # Set the initial position and scale.
    obj.setPos(pos.getX(), depth, pos.getY())
    obj.setScale(scale)

    # This tells Panda not to worry about the order that things are drawn in
    # (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
    obj.setBin("unsorted", 0)
    obj.setDepthTest(False)

    #if velocity != 0:
     #   obj.setVelocity(obj, velocity)

    if transparency:
        # Enable transparency blending.
        obj.setTransparency(TransparencyAttrib.MAlpha)

    if tex:
        # Load and set the requested texture.
        tex = loader.loadTexture("textures/" + tex)
        tex.setWrapU(SamplerState.WM_clamp)
        tex.setWrapV(SamplerState.WM_clamp)
        obj.setTexture(tex, 1)

    return obj


# Macro-like function used to reduce the amount to code needed to create the
# on screen instructions
def genLabelText(text, i):
    return OnscreenText(text=text, parent=base.a2dTopLeft, pos=(0.07, -.06 * i - 0.1),
                        fg=(1, 1, 1, 1), align=TextNode.ALeft, shadow=(0, 0, 0, 0.5), scale=.05)


class overFinger(ShowBase):

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        
        ShowBase.__init__(self)

        # This code puts the standard title and instruction text on screen
        self.title = OnscreenText(text="OverFinger",
                                  parent=base.a2dBottomRight, scale=.07,
                                  align=TextNode.ARight, pos=(-0.1, 0.1),
                                  fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5))
        """self.escapeText = genLabelText("ESC: Quit", 0)
        self.leftkeyText = genLabelText("[Left Arrow]: Turn Left (CCW)", 1)
        self.rightkeyText = genLabelText("[Right Arrow]: Turn Right (CW)", 2)
        self.upkeyText = genLabelText("[Up Arrow]: Accelerate", 3)
        self.spacekeyText = genLabelText("[Space Bar]: Fire", 4)"""

        # Disable default mouse-based camera control.  This is a method on the
        # ShowBase class from which we inherit.
        self.disableMouse()
        #I use the disable to disable the disable
        #HEALTH = 20 # Do you really need comments for this?
        # Load the background balls
        self.setBackgroundColor(255, 255, 255)
        self.bg = loadObject("nice cock.png", scale=30, depth=40,
                            transparency=True, velocity=0)
        
        # Load the ship and set its initial velocity.
        self.ship = loadObject("hart.png", velocity=2)
        velocity = 0
        headingr = self.ship.getR()
        head = headingr * DEG_TO_RAD
        delt = globalClock.getDt()
        self.setVelocity(self.ship, LVector3(sin(head), 0, cos(head)) * velocity * delt)

        # A dictionary of what keys are currently being pressed
        # The key events update this list, and our task will query it as input
        self.keys = {"turnLeft": 0, "turnRight": 0,
                     "accel": 0, "fire": 0,
                     "brake" : 0, "newScreen" : 0}

        self.accept("escape", sys.exit)  # Escape quits
        #IMPORTANT REMINDER : The keys that say -up are for when they ARE NOT pressed in
        # Other keys events set the appropriate value in our key dictionary
        self.accept("p", self.setKey, ["newScreen", 1])
        self.accept("p-up", self.setKey, ["newScreen", 0])
        self.accept("c", self.setKey, ["brake", 1])
        self.accept("c-up", self.setKey, ["brake" , 0])
        self.accept("arrow_left",     self.setKey, ["turnLeft", 1])
        self.accept("arrow_left-up",  self.setKey, ["turnLeft", 0])
        self.accept("arrow_right",    self.setKey, ["turnRight", 1])
        self.accept("arrow_right-up", self.setKey, ["turnRight", 0])
        self.accept("arrow_up",       self.setKey, ["accel", 1])
        self.accept("arrow_up-up",    self.setKey, ["accel", 0])
        self.accept("z",          self.setKey, ["fire", 1])
        
        
        # Now we create the task. taskMgr is the task manager that actually
        # calls the function each frame. The add method creates a new task.
        # The first argument is the function to be called, and the second
        # argument is the name for the task.  It returns a task object which
        # is passed to the function each frame.
        self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
        #self.gameTask = taskMgr.add(self.PL_INV)
        # Stores the time at which the next bullet may be fired.
        self.nextBullet = 0.0

        # This list will stored fired bullets.
        self.bullets = []

        # Complete initialization by spawning the asteroids.
        self.spawnAttacks()

    # As described earlier, this simply sets a key in the self.keys dictionary
    # to the given value.
    def setKey(self, key, val):
        self.keys[key] = val

    def setVelocity(self, obj, val):
        obj.setPythonTag("velocity", val)

    def getVelocity(self, obj):
        return obj.getPythonTag("velocity")

    def setExpires(self, obj, val):
        obj.setPythonTag("expires", val)

    def getExpires(self, obj):
        return obj.getPythonTag("expires")

    def spawnAttacks(self):
        # Control variable for if the ship is alive
        self.alive = True
        self.asteroids = []  # List that will contain our asteroids

        for i in range(50):# CHANGE THIS SHIT BACK THIS IS ONLY SET TO 1 FOR DEBUGGING PURPOSES
            # This loads a bomb. The texture chosen is random
            # from "bomb1.png" to "bomb2.png".
            asteroid = loadObject("bomb%d.png" % (randint(1, 2)),
                                  scale=AST_INIT_SCALE)
            self.asteroids.append(asteroid)

            # This is kind of a hack, but it keeps the asteroids from spawning
            # near the player.  It creates the list (-20, -19 ... -5, 5, 6, 7,
            # ... 20) and chooses a value from it. Since the player starts at 0
            # and this list doesn't contain anything from -4 to 4, it won't be
            # close to the player.
            asteroid.setX(choice(tuple(range(-SCREEN_X, -2)) + tuple(range(5, SCREEN_X))))
            # Same thing for Y
            asteroid.setZ(choice(tuple(range(-SCREEN_Y, -3)) + tuple(range(5, SCREEN_Y))))

            # Heading is a random angle in radians
            #The previous comment was a lie, this is in terms of pi, not even close to radians, which would be multiplying the num by 180/pi
            heading = random() * 2 * pi

            # Converts the heading to a vector and multiplies it by speed to
            # get a velocity vector
            v = LVector3(sin(heading), 0, cos(heading)) * AST_INIT_VEL
            self.setVelocity(self.asteroids[i], v)

    # This is our main task function, which does all of the per-frame
    # processing.  It takes in self like all functions in a class, and task,
    # the task object returned by taskMgr.
    def gameLoop(self, task):
        # Get the time elapsed since the next frame.  We need this for our
        # distance and velocity calculations.
        dt = globalClock.getDt()

        # If the ship is not alive, do nothing.  Tasks return Task.cont to
        # signify that the task should continue running. If Task.done were
        # returned instead, the task would be removed and would no longer be
        # called every frame.
        
        
        #Returning it in this frame causes an error and idk why.
        #Possible fixes : Having it revealed in a dream after taking 40 bennys
        
        while not self.alive:
            global HEALTH
            global HEALTH_REF
            if HEALTH == HEALTH_REF:
                HEALTH = HEALTH - 0.01325
                print(HEALTH)
                return task.cont
            else:
                HEALTH_REF = HEALTH
                return task.cont
        print(math.floor(HEALTH))
        
        
        
        # update ship position
        
        self.updateShip(dt)

        if self.keys["newScreen"]:
            #dialog = OkDialog(dialogName="help", text="sorry you're on your own", command=closeDialog)
            self.bg = loadObject("same.png", scale=30, depth=40, transparency=False)
            self.ship = loadObject("hart.png")
            self.setVelocity(self.ship, LVector3.zero())
        # check to see if the ship can fire
        if self.keys["fire"] and task.time > self.nextBullet:
            self.fire(task.time)  # If so, call the fire function
            # And disable firing for a bit
            self.nextBullet = task.time + BULLET_REPEAT
        # Remove the fire flag until the next spacebar press
        self.keys["fire"] = 0

        # update asteroids
        for obj in self.asteroids:
            self.updatePos2(obj, dt)

        # update bullets
        newBulletArray = []
        for obj in self.bullets:
            self.updatePos2(obj, dt)  # Update the bullet
            # Bullets have an experation time (see definition of fire)
            # If a bullet has not expired, add it to the new bullet list so
            # that it will continue to exist.
            if self.getExpires(obj) > task.time:
                newBulletArray.append(obj)
            else:
                obj.removeNode()  # Otherwise, remove it from the scene.
        # Set the bullet array to be the newly updated array
        self.bullets = newBulletArray

        # Check bullet collision with asteroids
        # In short, it checks every bullet against every asteroid. This is
        # quite slow.  A big optimization would be to sort the objects left to
        # right and check only if they overlap.  Framerate can go way down if
        # there are many bullets on screen, but for the most part it's okay.
        for bullet in self.bullets:
            # This range statement makes it step though the asteroid list
            # backwards.  This is because if an asteroid is removed, the
            # elements after it will change position in the list.  If you go
            # backwards, the length stays constant.
            for i in range(len(self.asteroids) -1, -1, -1):
                asteroid = self.asteroids[i]
                # Panda's collision detection is more complicated than we need
                # here.  This is the basic sphere collision check. If the
                # distance between the object centers is less than sum of the
                # radii of the two objects, then we have a collision. We use
                # lengthSquared() since it is faster than length().
                if ((bullet.getPos() - asteroid.getPos()).lengthSquared() <
                    (((bullet.getScale().getX() + asteroid.getScale().getX())
                      * .360) ** 2)):
                    # Schedule the bullet for removal
                    self.setExpires(bullet, 0)
                    self.asteroidHit(i)      # Handle the hit

        # Now we do the same collision pass for the ship
        shipSize = self.ship.getScale().getX()

        for ast in self.asteroids:
            # Same sphere collision check for the ship vs. the asteroid
            if ((self.ship.getPos() - ast.getPos()).lengthSquared() <
                    (((shipSize + ast.getScale().getX()) * .360) ** 2)): #THIS CODE IS VERY IMPORTANT IDK HOW IT WORKS I FORGOT BUT IT FUCKS WITH THE HITBOXES OF THE BOMBS AND I ACCIDENTALLY MADE THEM 300X BIGGER DON'T TOUCH
                # If there is a hit, clear the screen and schedule a restart
                self.alive = False
                
                # Ship is no longer alive
                # Remove every object in asteroids and bullets from the scene

                for i in self.asteroids + self.bullets:
                    i.removeNode()
                self.bullets = []          # Clear the bullet list
                #self.ship.hide()           # Hide the ship
                # Reset the velocity
                self.setVelocity(self.ship, LVector3(0, 0, 0))
                Sequence(Wait(2),          # Wait 2 seconds
                         Func(self.ship.setR, 0),  # Reset heading
                         Func(self.ship.setX, 0),  # Reset position X
                         # Reset position Y (Z for Panda)
                         Func(self.ship.setZ, 0),
                         Func(self.ship.show),     # Show the ship
                         Func(self.spawnAttacks)).start()  # Remake asteroids
                return Task.cont

        # If the player has successfully destroyed all asteroids, respawn them
        #Not anymore
        if len(self.asteroids) == 0:
            self.spawnAttacks()
            
            
        if math.floor(HEALTH) == 0:
            print("You died stoopid idoit")
            return Task.done
        

        return Task.cont    # Since every return is Task.cont, the task will
        # continue indefinitely

    def updatePos2(self, obj, dt):
        
        #for every new screen, use dataloop for attackSpawner to reset chracter
        # Check if the object is out of bounds. If so, wrap it
        """
        if(obj.getPos() = self.asteroids[index]):
            radius = .5 * obj.getScale().getX()
            if newPos.getX() - radius > SCREEN_X:
                self.bg = loadObject("same.png", scale = 30, depth = 40, transparency=False)
                newPos.setX(-SCREEN_X)
            elif newPos.getX() + radius < -SCREEN_X:
                newPos.setX(SCREEN_X)
            if newPos.getZ() - radius > SCREEN_Y:
                newPos.setZ(-SCREEN_Y)
            elif newPos.getZ() + radius < -SCREEN_Y:
                newPos.setZ(SCREEN_Y)
        """
        vel2 = self.getVelocity(obj)
        newPos = obj.getPos() + (vel2 * dt)
        #for ast in self.asteroids():
        radius = .5 * obj.getScale().getX()
        if newPos.getX() - radius > SCREEN_X:
            newPos.setX(-SCREEN_X)
        elif newPos.getX() + radius < -SCREEN_X:
            newPos.setX(SCREEN_X)
        if newPos.getZ() - radius > SCREEN_Y:
            newPos.setZ(-SCREEN_Y)
        elif newPos.getZ() + radius < -SCREEN_Y:
            newPos.setZ(SCREEN_Y)
        

        obj.setPos(newPos)
    # Updates the positions of objects
    def updatePos(self, obj, dt):
        vel = self.getVelocity(obj)
        newPos = obj.getPos() + (vel * dt)
        heading = self.ship.getR()
        heading_rad = DEG_TO_RAD * heading
        rg = LVector3(sin(heading_rad), 0, cos(heading_rad)) * ACCELERATION * dt
        rg += self.getVelocity(self.ship)
        #for every new screen, use dataloop for attackSpawner to reset chracter
        # Check if the object is out of bounds. If so, wrap it

        # Ignore this broken code it was for something I found a way around
        """
        if(obj.getPos() = self.asteroids[index]):
            radius = .5 * obj.getScale().getX()
            if newPos.getX() - radius > SCREEN_X:
                self.bg = loadObject("same.png", scale = 30, depth = 40, transparency=False)
                newPos.setX(-SCREEN_X)
            elif newPos.getX() + radius < -SCREEN_X:
                newPos.setX(SCREEN_X)
            if newPos.getZ() - radius > SCREEN_Y:
                newPos.setZ(-SCREEN_Y)
            elif newPos.getZ() + radius < -SCREEN_Y:
                newPos.setZ(SCREEN_Y)
        """

        radius = .5 * obj.getScale().getX()
        if newPos.getX() - radius > SCREEN_X:
            self.bg = loadObject("same.png", scale = 30, depth = 40, transparency=False)
            self.ship = loadObject("hart.png")
            newPos.setX(-SCREEN_X)
        elif newPos.getX() + radius < -SCREEN_X:
            newPos.setX(SCREEN_X)
        if newPos.getZ() - radius > SCREEN_Y:
            newPos.setZ(-SCREEN_Y)
        elif newPos.getZ() + radius < -SCREEN_Y:
            newPos.setZ(SCREEN_Y)

        obj.setPos(newPos)

    # The handler when an asteroid is hit by a bullet
    def asteroidHit(self, index):
        # If the asteroid is small it is simply removed
        if (self.asteroids[index].getScale().getX()) <= AST_MIN_SCALE:
            self.asteroids[index].removeNode()
            # Remove the asteroid from the list of asteroids.
            del self.asteroids[index]
        else:
            # If it is big enough, divide it up into little asteroids.
            # First we update the current asteroid.
            asteroid = self.asteroids[index]
            newScale = asteroid.getScale().getX() * AST_SIZE_SCALE
            asteroid.setScale(newScale)  # Rescale it

            # The new direction is chosen as perpendicular to the old direction
            # This is determined using the cross product, which returns a
            # vector perpendicular to the two input vectors.  By crossing
            # velocity with a vector that goes into the screen, we get a vector
            # that is orthagonal to the original velocity in the screen plane.
            vel = self.getVelocity(asteroid)
            speed = vel.length() * AST_VEL_SCALE
            vel.normalize()
            vel = LVector3(0, 1, 0).cross(vel)
            vel *= speed
            self.setVelocity(asteroid, vel)

            # Now we create a new asteroid identical to the current one
            newAst = loadObject(scale=newScale)
            self.setVelocity(newAst, vel * -1)
            newAst.setPos(asteroid.getPos())
            newAst.setTexture(asteroid.getTexture(), 1)
            self.asteroids.append(newAst)

    # This updates the ship's position. This is similar to the general update
    # but takes into account turn and thrust
    def updateShip(self, dt):
        heading = self.ship.getR()  # Heading is the roll value for this model
        # Change heading if left or right is being pressed
        if self.keys["turnRight"]:
            heading += dt * TURN_RATE
            self.ship.setR(heading % 360)
        elif self.keys["turnLeft"]:
            heading -= dt * TURN_RATE
            self.ship.setR(heading % 360)

        # Thrust causes acceleration in the direction the ship is currently
        # facing
        if self.keys["accel"] and not self.keys["brake"]:
            heading_rad = DEG_TO_RAD * heading
            # This builds a new velocity vector and adds it to the current one
            # relative to the camera, the screen in Panda is the XZ plane.
            # Therefore all of our Y values in our velocities are 0 to signify
            # no change in that direction.
            newVel = LVector3(sin(heading_rad), 0, cos(heading_rad)) * ACCELERATION * dt
            """This one line of code breaks everything idk why tho"""
            newVel += self.getVelocity(self.ship)
            # Clamps the new velocity to the maximum speed. lengthSquared() is
            # used again since it is faster than length()
            if newVel.lengthSquared() > MAX_VEL_SQ:
                newVel.normalize()
                newVel *= MAX_VEL
            self.setVelocity(self.ship, newVel)
        elif self.keys["brake"]:
            heading_rad = DEG_TO_RAD * heading
            velo = LVector3(sin(heading_rad), 0, cos(heading_rad)) * ACCELERATION * dt
            velo += self.getVelocity(self.ship)
            self.setVelocity(self.ship, velo*.95)
        # Finally, update the position as with any other object
        # We use dt because it updates every other frame, which is the fastest we can get without killing pyhton
        self.updatePos(self.ship, dt)

    # Creates a bullet and adds it to the bullet list
    def fire(self, time):
        direction = DEG_TO_RAD * self.ship.getR()
        pos = self.ship.getPos()
        bullet = loadObject("boolet.png", scale=.2)  # Create the object
        bullet.setPos(pos)
        # Velocity is in relation to the ship
        vel = (self.getVelocity(self.ship) + (LVector3(sin(direction), 0, cos(direction)) * BULLET_SPEED))
        self.setVelocity(bullet, vel)
        # Set the bullet expiration time to be a certain amount past the
        # current time
        self.setExpires(bullet, time + BULLET_LIFE)

        # Finally, add the new bullet to the list
        self.bullets.append(bullet)

# We now have everything we need. Make an instance of the class and start
# 3D rendering
game = overFinger()
game.run()
