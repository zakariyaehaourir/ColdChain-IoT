#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include "secrets.h"

#define DHTPIN D2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

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
  Serial.print("wildmask: ");
  Serial.println(WiFi.subnetMask());
  Serial.printf("Signal Wi-Fi: %d dBm\n", WiFi.RSSI());
  Serial.printf("Remote Server: %s\n", SERVER_URL);
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println();
  Serial.println("Starting ESP capture...");

  dht.begin();
  connectToWiFi();
}

void loop() {
  if (!connectToWiFi()) {
    delay(SEND_INTERVAL_MS);
    return;
  }

  const float temperature = dht.readTemperature();
  const float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error DHT11.");
    delay(SEND_INTERVAL_MS);
    return;
  }

  Serial.printf("Temp: %.1f C | Hum: %.1f %%\n",
                temperature, humidity);

  WiFiClient client;
  HTTPClient http;

  if (!http.begin(client, SERVER_URL)) {
    Serial.println("Error HTTP: cannot etablish a connexion.");
    delay(SEND_INTERVAL_MS);
    return;
  }

  http.setTimeout(30000);
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"temp\":";
  payload += String(temperature, 1);
  payload += ",\"hum\":";
  payload += String(humidity, 1);
  payload += "}";

  Serial.printf("POST %s\n", SERVER_URL);
  Serial.printf("JSON: %s\n", payload.c_str());

  const int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("HTTP Response: %d\n", httpCode);
    Serial.printf("BODY: %s\n", http.getString().c_str());
    if (httpCode < 200 || httpCode >= 300) {
      Serial.println("500 Error from the server");
    }
  } else {
    Serial.printf("HTTP Error: %s (code %d)\n",
                  http.errorToString(httpCode).c_str(), httpCode);
  }

  http.end();
  delay(SEND_INTERVAL_MS);
}
