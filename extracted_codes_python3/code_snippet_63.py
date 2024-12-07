def Level2():
    from message import crashed
    import turtle
    import time
    import random
    from pygame import mixer
    delay = 0.04

    # score
    score = 0
    high_score = 0

    # set up screen
    wn = turtle.Screen()
    wn.title("snake bite")
    wn.bgcolor("black")
    wn.setup(width=1370, height= 690)
    wn.tracer(0)
    wn.bgpic("cover.gif")
    wn.addshape("apple.gif")
    wn.addshape(
        "upmouth.gif")  # Here we have given command to add shape  to thw window, and we use image in the form of gif
    wn.addshape(
        "rightmouth.gif")  # Here we have given command to add shape  to thw window, and we use image in the form of gif
    wn.addshape(
        "leftmouth.gif")  # Here we have given command to add shape  to thw window, and we use image in the form of gif
    wn.addshape(
        "downmouth.gif")  # Here we have given command to add shape  to thw window, and we use image in the form of gif
    wn.addshape("body.gif")

    # Background music
    mixer.init()
    mixer.music.load("Snake.wav")
    mixer.music.play(-1)

    # Snake head
    head = turtle.Turtle()
    head.speed(0)
    head.shape("upmouth.gif")
    head.color("black")
    head.penup()
    head.goto(0, -250)
    head.shapesize(1.3)

    head.direction = "stop"

    pen0 = turtle.Turtle()
    pen0.speed(0)
    pen0.shape("circle")
    pen0.color("black")
    pen0.penup()
    pen0.hideturtle()
    pen0.goto(0, -150)
    pen0.write("""
     ⬅️key to go left
     ➡️key to go right
     ⬇️key to go down
     ⬆️key to go up
    
        """, align="center", font=("courier", 24, "normal"))
    time.sleep(3)
    pen0.clear()
    pen0.goto(0, -10)
    pen0.write("👉start👈", align="center", font=("courier", 30, "normal"))
    time.sleep(2)
    pen0.clear()

    # snake food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("apple.gif")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    segments = []

    # pen
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("circle")
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(400, 190)
    pen.write("""
        Score: 0    
        High Score: 0
            """, align="center", font=("courier", 24, "normal"))

    pen1 = turtle.Turtle()
    pen1.hideturtle()
    pen1.pencolor("black")
    pen1.goto(-300, 250)
    pen1.clear()
    for i in range(2):
        pen1.forward(100)
        pen1.left(90)
        pen1.forward(30)
        pen1.left(90)
    pen1.penup()
    pen1.write("🏠Home", font=("courier", 20, "normal"), align="left")

    pen2 = turtle.Turtle()
    pen2.speed(0)
    pen2.shape("circle")
    pen2.color("black")
    pen2.penup()
    pen2.hideturtle()
    pen2.goto(380, 100)
    pen2.write("""
           🪜 LEVEL-2
               """, align="center", font=("courier", 30, "normal"))


    def buttonClick(x, y):
        global colorvar
        if x > -300 and x < -215 and y > 250 and y < 290:
            wn.bye()
            crashed()

    wn.onscreenclick(buttonClick, 1)
    wn.listen()

    # Functions
    def go_up():
        if head.direction != "down":
            head.direction = "up"
            head.shape("upmouth.gif")
            up = mixer.Sound("move1.wav")
            up.play()

    def go_down():
        if head.direction != "up":
            head.direction = "down"
            head.shape("downmouth.gif")
            down = mixer.Sound("move2.wav")
            down.play()

    def go_left():
        if head.direction != "right":
            head.direction = "left"
            head.shape("leftmouth.gif")
            right = mixer.Sound("move3.wav")
            right.play()

    def go_right():
        if head.direction != "left":
            head.direction = "right"
            head.shape("rightmouth.gif")
            left = mixer.Sound("move4.wav")
            left.play()

    def move():
        if head.direction == "up":
            head.sety(head.ycor() + 20)
        if head.direction == "down":
            head.sety(head.ycor() - 20)
        if head.direction == "right":
            head.setx(head.xcor() + 20)
        if head.direction == "left":
            head.setx(head.xcor() - 20)

    # keyboard
    wn.listen()
    wn.onkeypress(go_up, "Up")
    wn.onkeypress(go_down, "Down")
    wn.onkeypress(go_left, "Left")
    wn.onkeypress(go_right, "Right")

    # Main game Loop
    while True:
        wn.update()
        # border collisions
        if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 280 or head.ycor() < -280:
            time.sleep(0.1)
            end = mixer.music.load("crashed.wav")
            mixer.music.play()
            pen4 = turtle.Turtle()
            pen4.speed(0)
            pen4.shape("circle")
            pen4.color("black")
            pen4.penup()
            pen4.hideturtle()
            pen4.goto(0, 0)
            pen4.write("GAME OVER", align="center", font=("courier", 30, "normal"))
            time.sleep(0.5)
            wn.bye()
            crashed()
            head.goto(0, -250)
            head.direction = "stop"
            # hiding segments
            for segment in segments:
                segment.goto(10000, 10000)

            # clearing segments
            segments.clear()

            score = 0

            # reset Background music
            time.sleep(0.5)
            mixer.init()
            mixer.music.load("Snake2.wav")
            mixer.music.play(-1)

            pen.clear()
            pen.write(f"""
        score: {score}  
        High score: {high_score}
                    """.format(score, high_score), align="center", font=("courier", 24, "normal"))

        if head.distance(food) < 20:
            x = random.randrange(-285, 285, 20)
            y = random.randrange(-275, 275, 20)
            food.goto(x, y)
            bite = mixer.Sound("bite.wav")
            bite.play()

            # SEGMENTS
            new_segemnt = turtle.Turtle()
            new_segemnt.speed(0)
            new_segemnt.shape("body.gif")
            new_segemnt.color("grey")
            new_segemnt.penup()
            segments.append(new_segemnt)
            # score
            score += 1

            if score > high_score:
                high_score = score

            pen.clear()
            pen.write(f"""
        score: {score}  
        High score: {high_score}
                    """.format(score, high_score), align="center", font=("courier", 24, "normal"))

        # moving segemnt along head
        for index in range(len(segments) - 1, 0, -1):
            x = segments[index - 1].xcor()
            y = segments[index - 1].ycor()
            segments[index].goto(x, y)

        # segment 0
        if len(segments) > 0:
            x = head.xcor()
            y = head.ycor()
            segments[0].goto(x, y)

        move()

        # body collisions
        for segment in segments:
            if segment.distance(head) < 20:
                end = mixer.music.load("crashed.wav")
                mixer.music.play()
                pen4 = turtle.Turtle()
                pen4.speed(0)
                pen4.shape("circle")
                pen4.color("black")
                pen4.penup()
                pen4.hideturtle()
                pen4.goto(0, 0)
                pen4.write("GAME OVER", align="center", font=("courier", 30, "normal"))
                wn.bye()
                crashed()
                time.sleep(0.1)
                head.goto(0, -250)
                head.direction = "stop"

                # hiding segments
                for segment in segments:
                    segment.goto(10000, 10000)

                # clearing segments
                segments.clear()

                # update of score
                score = 0

                # reset bgm
                time.sleep(0.5)
                mixer.init()
                mixer.music.load("Snake2.wav")
                mixer.music.play(-1)

                pen.clear()
                pen.write(f"""
            score: {score}  
            High score: {high_score}
                        """.format(score, high_score), align="left", font=("courier", 24, "normal"))
        time.sleep(delay)
    wn.mainloop()
