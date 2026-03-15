#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "Airtel_56";
const char* password = "Raviuma5658";

String server = "https://mahajanesp6a.streamlit.app/?heartbeat=1";

unsigned long lastHB = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi Connected");
}

void loop() {

  if (millis() - lastHB > 5000) {

    if (WiFi.status() == WL_CONNECTED) {

      HTTPClient http;
      http.begin(server);

      int httpCode = http.GET();

      Serial.print("Heartbeat response: ");
      Serial.println(httpCode);

      http.end();
    }

    lastHB = millis();
  }
}
