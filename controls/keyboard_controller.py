import pygame
import can

pygame.init()

screen = pygame.display.set_mode((600, 350))
pygame.display.set_caption("Automotive Digital Twin - Keyboard Controller")

font = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()

bus = can.Bus(channel="vcan0", interface="socketcan")

speed = 0.0
steering = 0
engine_on = True
running = True

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_s:
                    engine_on = not engine_on

                elif event.key == pygame.K_SPACE:
                    speed = 0

        keys = pygame.key.get_pressed()

        if engine_on:
            if keys[pygame.K_UP]:
                speed += 0.5
            elif keys[pygame.K_DOWN]:
                speed -= 1.0
            else:
                speed -= 0.1
        else:
            speed = 0

        speed = max(0, min(120, speed))

        if keys[pygame.K_LEFT]:
            steering = -30
        elif keys[pygame.K_RIGHT]:
            steering = 30
        else:
            steering = 0

        rpm = int(800 + speed * 25) if engine_on else 0

        # CAN ID 0x300: controller command
        data = [
            int(speed),
            rpm & 0xFF,
            (rpm >> 8) & 0xFF,
            steering + 30,
            int(engine_on),
            0,
            0,
            0
        ]

        message = can.Message(
            arbitration_id=0x300,
            data=data,
            is_extended_id=False
        )

        bus.send(message)

        screen.fill((15, 20, 30))

        lines = [
            "AUTOMOTIVE DIGITAL TWIN",
            f"Speed: {speed:.1f} km/h",
            f"RPM: {rpm}",
            f"Steering: {steering} degrees",
            f"Engine: {'ON' if engine_on else 'OFF'}",
            "Arrows: Drive | S: Engine | Space: Stop"
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 255, 220))
            screen.blit(text, (30, 30 + i * 45))

        pygame.display.flip()
        clock.tick(20)

finally:
    # Send a safe stop command on exit
    try:
        stop_message = can.Message(
            arbitration_id=0x300,
            data=[0, 0, 0, 30, 0, 0, 0, 0],
            is_extended_id=False
        )
        bus.send(stop_message)
    finally:
        bus.shutdown()
        pygame.quit()
