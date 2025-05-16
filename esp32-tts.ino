#include "WiFi.h"
#include "HTTPClient.h"
#include "Audio.h"
#include "WebServer.h"
#include "ArduinoJson.h"

// WiFi credentials
const char* ssid = "";
const char* password = "";

#define I2S_DOUT  25  // Data Out Pin
#define I2S_BCLK  33  // Bit Clock Pin
#define I2S_LRC   32  // Left Right Clock Pin

Audio audio;
WebServer server(80);

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolume(21);
  
  server.on("/speak", HTTP_POST, handleSpeak);
  
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
  audio.loop();
}

void handleSpeak() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, body);
    
    if (error) {
      server.send(400, "text/plain", "Invalid JSON");
      return;
    }
    
    if (doc.containsKey("text")) {
      String text = doc["text"].as<String>();
    
      server.send(200, "text/plain", "Playing text: " + text);
      
      playLongText(text);
    } else {
      server.send(400, "text/plain", "Missing 'text' field in JSON");
    }
  } else {
    server.send(400, "text/plain", "No data received");
  }
}

void playLongText(String text) {
  int maxChunkSize = 200; // Google TTS max length
  int startPos = 0;
  
  Serial.println("Playing text: " + text);
  
  while (startPos < text.length()) {
    int endPos = min(startPos + maxChunkSize, (int)text.length());
    String chunk = text.substring(startPos, endPos);
    
    
    chunk.replace(" ", "%20");
    
    String tts_url = "http://translate.google.com/translate_tts?ie=UTF-8&q=" + chunk + "&tl=en&client=tw-ob";

    audio.connecttohost(tts_url.c_str());
    
    
    while (audio.isRunning()) {
      audio.loop();
      server.handleClient();
    }
    
    startPos = endPos;
    delay(500); 
  }
}