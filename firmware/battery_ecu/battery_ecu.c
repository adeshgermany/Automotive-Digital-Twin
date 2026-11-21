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

    double voltage = 400.0;
    double current = 20.0;
    double temperature = 30.0;
    double soc = 90.0;

    double capacity = 60.0;
    double dt = 0.1;

    sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (sock < 0) {
        perror("Socket creation failed");
        return 1;
    }

    strcpy(ifr.ifr_name, "vcan0");

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("CAN interface error");
        close(sock);
        return 1;
    }

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr,
             sizeof(addr)) < 0) {
        perror("CAN bind failed");
        close(sock);
        return 1;
    }

    frame.can_id = 0x200;
    frame.can_dlc = 8;

    printf("Battery ECU Started\n");

    while (1)
    {
        // Coulomb counting
        soc = soc - (current * dt / (3600.0 * capacity)) * 100.0;

        if (soc < 0.0) {
            soc = 0.0;
        }

        // Encode battery signals
        uint16_t voltage_raw = (uint16_t)(voltage * 10.0);
        int16_t current_raw = (int16_t)(current * 10.0);
        uint16_t soc_raw = (uint16_t)(soc * 100.0);
        int16_t temp_raw = (int16_t)(temperature * 10.0);

        frame.data[0] = (voltage_raw >> 8) & 0xFF;
        frame.data[1] = voltage_raw & 0xFF;

        frame.data[2] = ((uint16_t)current_raw >> 8) & 0xFF;
        frame.data[3] = (uint16_t)current_raw & 0xFF;

        frame.data[4] = (soc_raw >> 8) & 0xFF;
        frame.data[5] = soc_raw & 0xFF;

        frame.data[6] = ((uint16_t)temp_raw >> 8) & 0xFF;
        frame.data[7] = (uint16_t)temp_raw & 0xFF;

        if (write(sock, &frame, sizeof(frame))
            != sizeof(frame)) {
            perror("CAN transmission failed");
            close(sock);
            return 1;
        }

        printf("Voltage: %.1f V | Current: %.1f A | "
               "SOC: %.4f %% | Temp: %.1f C\n",
               voltage, current, soc, temperature);

        usleep(100000);
    }

    close(sock);
    return 0;
}

