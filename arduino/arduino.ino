/*************************************************** 
  NodeMCU
****************************************************/ 
#include <ESP8266WiFi.h> 
#include "Adafruit_MQTT.h" 
#include "Adafruit_MQTT_Client.h" 
/************************* WiFi Access Point *********************************/ 
#define WLAN_SSID       "newton_room" 
#define WLAN_PASS       "abcd1234" 
#define MQTT_SERVER      "192.168.1.68" // static ip address
#define MQTT_PORT         1883                    
#define MQTT_USERNAME    "yoonhero" 
#define MQTT_PASSWORD         "" 

/************ Global State ******************/ 
// Create an ESP8266 WiFiClient class to connect to the MQTT server. 
WiFiClient client; 
// Setup the MQTT client class by passing in the WiFi client and MQTT server and login details. 
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD); 
/****************************** Feeds ***************************************/ 
// Setup a feed called 'pi_led' for publishing. 
// Notice MQTT paths for AIO follow the form: <username>/feeds/<feedname> 
Adafruit_MQTT_Publish pi_con = Adafruit_MQTT_Publish(&mqtt, MQTT_USERNAME "/con/pi"); 

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

int threshold_angle = 3000;
#define FORWARD "F"
#define BACKWARD "B"
#define LEFT "L"
#define RIGHT "R"
#define STOP "S"

/*************************** Sketch Code ************************************/ 
void MQTT_connect(); 
void setup() { 
    Serial.begin(115200); 
    delay(10); 
    pinMode(LED_PIN, OUTPUT); 
    digitalWrite(LED_PIN, LOW); 
    // Setup button as an input with internal pull-up. 
    pinMode(BUTTON_PIN, INPUT_PULLUP); 
    Serial.println(F("RPi-ESP-MQTT")); 
    // Connect to WiFi access point. 
    Serial.println(); Serial.println(); 
    Serial.print("Connecting to "); 
    Serial.println(WLAN_SSID); 
    WiFi.begin(WLAN_SSID, WLAN_PASS); 

    while (WiFi.status() != WL_CONNECTED) { 
        delay(500); 
        Serial.print("."); 
    } 

    Serial.println(); 
    Serial.println("WiFi connected"); 
    Serial.println("IP address: "); Serial.println(WiFi.localIP()); 

    Wire.begin();
    mpu.initialize();
    
    // Uncomment the following line to calibrate the sensor offsets
    // mpu.calibrateAccel(6);
    // mpu.calibrateGyro(6);
} 

uint32_t x=0; 
void loop() { 
    int16_t ax, ay, az;
    int16_t gx, gy, gz;
    
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    MQTT_connect(); 

    delay(20); 

    if (ay > threshold_angle){
        Serial.println("Forward"); 
        pi_con.public(FORWARD)
    } else if (-ay > threshold_angle){
        Serial.println("Backward"); 
        pi_con.public(BACKWARD)
    } else if (ax > threshold_angle){
        Serial.println("RIGHT"); 
        pi_con.public(RIGHT)
    } else if (-ax > threshold_angle){
        Serial.println("LEFT"); 
        pi_con.public(LEFT)   
    } else {
        Serial.println("STOP")
        pi_con.public(STOP)
    } 
} 
// Function to connect and reconnect as necessary to the MQTT server. 
void MQTT_connect() { 
    int8_t ret; 
    // Stop if already connected. 
    if (mqtt.connected()) { 
    return; 
    } 
    Serial.print("Connecting to MQTT... "); 
    uint8_t retries = 3; 
    while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected 
        Serial.println(mqtt.connectErrorString(ret)); 
        Serial.println("Retrying MQTT connection in 5 seconds..."); 
        mqtt.disconnect(); 
        delay(5000);  // wait 5 seconds 
        retries--; 
        if (retries == 0) { 
            // basically die and wait for WDT to reset me 
            while (1); 
        } 
    } 
    Serial.println("MQTT Connected!"); 
} 