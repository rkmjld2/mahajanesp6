#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

const char* ssid="Airtel_56";
const char* password="Raviuma5658";

String server="https://mahajanesp6.streamlit.app";

int relayPins[9]={16,5,4,0,2,14,12,13,15};

unsigned long lastCheck=0;

WiFiClientSecure client;

void setup()
{

Serial.begin(115200);

WiFi.begin(ssid,password);

while(WiFi.status()!=WL_CONNECTED)
{
delay(500);
Serial.print(".");
}

Serial.println("Connected");
Serial.println(WiFi.localIP());
client.setInsecure();

for(int i=0;i<8;i++)
{
pinMode(relayPins[i],OUTPUT);
}

}

void loop()
{

if(millis()-lastCheck>5000)
{

lastCheck=millis();

HTTPClient http;

/* heartbeat */

http.begin(client,server+"/heartbeat");
http.GET();
http.end();

/* read relay state */

http.begin(client,server+"/read");

int code=http.GET();

if(code==200)
{

String payload=http.getString();

for(int i=0;i<8;i++)
{

if(payload[i]=='G')
digitalWrite(relayPins[i],HIGH);
else
digitalWrite(relayPins[i],LOW);

}

}

http.end();

}

}
