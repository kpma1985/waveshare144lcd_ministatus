import LCD_1in44
import psutil
import RPi.GPIO as GPIO
from time import sleep, strftime, localtime
from PIL import Image, ImageDraw, ImageFont, ImageColor
import socket
import netifaces

def get_color_gradient(start_color, end_color, percentage):
    # Berechne den Farbverlauf zwischen den Start- und Endfarben basierend auf dem Prozentsatz
    r = int(start_color[0] + percentage * (end_color[0] - start_color[0]))
    g = int(start_color[1] + percentage * (end_color[1] - start_color[1]))
    b = int(start_color[2] + percentage * (end_color[2] - start_color[2]))
    return (r, g, b)

def get_ip_address(interface):
    try:
        addresses = netifaces.ifaddresses(interface)
        ipv4_address = addresses[netifaces.AF_INET][0]['addr']
        return ipv4_address
    except:
        return "Not available"

def display_bars(LCD, background_color="BLACK"):
    image = Image.new("RGB", (LCD.width, LCD.height), background_color)
    draw = ImageDraw.Draw(image)

    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent

    bar_height = int(LCD.height * 0.5)  # Verwende 50% der Höhe des Displays für die Balken

    # Farbverlauf von Grün nach Rot für den CPU-Balken
    start_color = (0, 255, 0)  # Grün
    end_color = (255, 0, 0)  # Rot
    cpu_color = get_color_gradient(start_color, end_color, cpu_percent / 100.0)

    # Breite des CPU-Balkens entsprechend CPU-Auslastung
    cpu_width = int(cpu_percent * (LCD.width / 100))

    # Zeichne den CPU-Balken in der linken Hälfte des Bildes
    draw.rectangle((0, LCD.height - bar_height, cpu_width, LCD.height), fill=cpu_color)

    # Farbverlauf von Grün nach Rot für den Memory-Balken
    memory_color = get_color_gradient(start_color, end_color, memory_percent / 100.0)

    # Breite des Memory-Balkens entsprechend Speicherauslastung
    memory_width = int(memory_percent * (LCD.width / 100))

    # Zeichne den Memory-Balken in der rechten Hälfte des Bildes
    draw.rectangle((LCD.width - memory_width, LCD.height - bar_height, LCD.width, LCD.height), fill=memory_color)

    # Verwende eine Schriftart und Schriftgröße 12
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 12)

    # Zeichne Text für CPU und Memory in weißer Farbe, oben links auf dem Bildschirm
    cpu_text = "CPU: {}%".format(cpu_percent)
    draw.text((5, 5), cpu_text, fill="WHITE", font=font)

    # Zeichne Text für Memory
    memory_text = "Memory: {}%".format(memory_percent)
    draw.text((5, 20), memory_text, fill="WHITE", font=font)

    # Verwende eine kleinere Schriftart für die IP-Adresse
    ip_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 10)

    # Zeichne die IP-Adresse unten links auf dem Bildschirm
    ip_address = "IPv4: " + get_ip_address("eth0")
    draw.text((5, LCD.height - 80), ip_address, fill="WHITE", font=ip_font)

    # Verwende eine kleinere Schriftart für die Uhrzeit
    time_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 8)

    # Zeichne die aktuelle Uhrzeit oben rechts auf dem Bildschirm
    current_time = strftime("%H:%M:%S", localtime())
    draw.text((LCD.width - 40 ,0,10 ), current_time, fill="WHITE", font=time_font)

    LCD.LCD_ShowImage(image, 0, 0)

def main():
    GPIO.setmode(GPIO.BCM)
    buttons = [6, 19, 5, 26, 13, 21, 20, 16]
    for button in buttons:
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    LCD = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    LCD.LCD_Init(Lcd_ScanDir)
    LCD.LCD_Clear()

    background_color = "BLACK"

    try:
        while True:
            for button in buttons:
                if GPIO.input(button) == GPIO.LOW:
                    if button == 21:
                        if background_color == "BLACK":
                            background_color = "GRAY"
                        else:
                            background_color = "BLACK"
                        display_bars(LCD, background_color)
                        sleep(0.2)  # Kurze Verzögerung, um mehrfaches Drücken zu verhindern

            display_bars(LCD, background_color)
            sleep(1)  # Aktualisiere die Anzeige

    except KeyboardInterrupt:
        pass
    finally:
        LCD.LCD_Clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()

