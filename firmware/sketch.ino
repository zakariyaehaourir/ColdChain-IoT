#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "secrets.h"

#define DHTPIN D2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

const unsigned long WIFI_TIMEOUT_MS = 20000;
const unsigned long SEND_INTERVAL_MS = 5000;

bool connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  Serial.printf("Try to connect to WIFI ...\"%s\"...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  const unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - startTime < WIFI_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("Cannot connect to WIFI with code: %d\n", WiFi.status());
    return false;
  }

  Serial.println("Wi-Fi Connected.");
  Serial.print("Adresse IP ESP: ");
  Serial.println(WiFi.localIP());
  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());
  Serial.print("Subnet mask: ");
  Serial.println(WiFi.subnetMask());
  Serial.printf("Wi-Fi signal: %d dBm\n", WiFi.RSSI());
  Serial.printf(
      "MQTT broker: %s:%u\n",
      MQTT_BROKER_HOST,
      static_cast<unsigned int>(MQTT_BROKER_PORT));
  return true;
}

bool connectToMqtt() {
  if (mqttClient.connected()) {
    return true;
  }

  String clientId = "ColdChainESP8266-";
  clientId += String(ESP.getChipId(), HEX);

  Serial.printf("Connecting to MQTT broker %s:%u...\n",
                MQTT_BROKER_HOST,
                static_cast<unsigned int>(MQTT_BROKER_PORT));
  if (mqttClient.connect(clientId.c_str())) {
    Serial.println("Connected to MQTT broker.");
    return true;
  }

  Serial.printf("MQTT connection failed with state %d.\n", mqttClient.state());
  return false;
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println();
  Serial.println("Starting ESP capture...");

  dht.begin();
  mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
  connectToWiFi();
}

void loop() {
  if (!connectToWiFi()) {
    delay(SEND_INTERVAL_MS);
    return;
  }

  if (!connectToMqtt()) {
    delay(SEND_INTERVAL_MS);
    return;
  }

  mqttClient.loop();

  const float temperature = dht.readTemperature();
  const float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error DHT11.");
    delay(SEND_INTERVAL_MS);
    return;
  }

  Serial.printf("Temp: %.1f C | Hum: %.1f %%\n",
                temperature, humidity);

  char payload[64];
  snprintf(
      payload,
      sizeof(payload),
      "{\"temp\":%.1f,\"hum\":%.1f}",
      temperature,
      humidity);

  if (mqttClient.publish(MQTT_TOPIC, payload)) {
    Serial.printf("Published to topic %s: %s\n", MQTT_TOPIC, payload);
  } else {
    Serial.printf("Failed to publish to topic %s (MQTT state %d).\n",
                  MQTT_TOPIC, mqttClient.state());
  }

  mqttClient.loop();
  delay(SEND_INTERVAL_MS);
}
