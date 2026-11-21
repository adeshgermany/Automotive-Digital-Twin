#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int main(void)
{
    int sock;
    struct sockaddr_can addr = {0};
    struct ifreq ifr = {0};
    struct can_frame frame = {0};

    uint16_t speed = 0;
    uint16_t rpm = 800;
    uint8_t temperature = 85;

    sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (sock < 0) {
        perror("Socket error");
        return 1;
    }

    strcpy(ifr.ifr_name, "vcan0");

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("Interface error");
        close(sock);
        return 1;
    }

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr,
             sizeof(addr)) < 0) {
        perror("Bind error");
        close(sock);
        return 1;
    }

    frame.can_id = 0x100;
    frame.can_dlc = 8;

    printf("Engine ECU Started\n");

    while (1)
    {
        rpm = 800 + speed * 25;

        frame.data[0] = speed >> 8;
        frame.data[1] = speed & 0xFF;

        frame.data[2] = rpm >> 8;
        frame.data[3] = rpm & 0xFF;

        frame.data[4] = temperature;
        frame.data[5] = 1;
        frame.data[6] = 0;
        frame.data[7] = 0;

        if (write(sock, &frame, sizeof(frame))
            != sizeof(frame)) {
            perror("CAN transmission error");
            close(sock);
            return 1;
        }

        printf("Speed: %u km/h | RPM: %u | Temp: %u C\n",
               (unsigned)speed,
               (unsigned)rpm,
               (unsigned)temperature);

        speed = (speed + 5) % 125;

        usleep(100000);
    }

    close(sock);
    return 0;
}
