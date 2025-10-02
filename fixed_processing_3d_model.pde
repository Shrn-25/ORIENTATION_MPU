

//sharon_try_5

/*
FIXED Processing 3D Model Control - Responsive IMU Control
Addresses lag and orientation mapping issues
*/


import processing.serial.*;



import java.io.BufferedReader;
import java.io.IOException;

// 3D Model
PShape model;
String modelFile = "drone_costum.obj";
boolean modelLoaded = false;
float modelScale = 80.0;

// Serial communication
Serial myPort;
boolean serialConnected = false;
String serialBuffer = "";

// Rotation control - FIXED for responsiveness
float rotX = 0, rotY = 0, rotZ = 0;
float targetX = 0, targetY = 0, targetZ = 0;

// Control modes
boolean manualControl = false;
boolean demoMode = false;
boolean fastMode = true;  // NEW: Skip smoothing for real-time response
float demoTime = 0;
float smoothing = 0.3;    // INCREASED from 0.1 for faster response

// Debug info
boolean showDebugValues = true;
float lastSerialTime = 0;
int serialDataCount = 0;

void setup() {
  size(1200, 800, P3D);

  // Try to load 3D model
  loadModel();

  // Initialize serial
  initSerial();

  println("🎮 FIXED 3D MODEL CONTROLS:");
  println("📡 SERIAL: Connect Arduino with IMU");
  println("⚡ FAST MODE: Real-time response (F key)");
  println("🐛 DEBUG: Live serial values (V key)");
  println("");
  println("CONTROLS:");
  println("M - Toggle manual control");
  println("D - Toggle demo mode");
  println("F - Toggle fast mode (no smoothing)");
  println("V - Toggle debug values display");
  println("R - Reset orientation");
  println("S - Toggle serial connection");
  println("+ / - - Scale model");
}

void draw() {
  background(30);
  lights();
  setupLighting();

  // Update rotation - IMPROVED
  updateRotation();

  // Apply smoothing only if not in fast mode
  if (fastMode) {
    // Direct assignment for immediate response
    rotX = targetX;
    rotY = targetY; 
    rotZ = targetZ;
  } else {
    // Smooth transitions
    rotX = lerp(rotX, targetX, smoothing);
    rotY = lerp(rotY, targetY, smoothing);
    rotZ = lerp(rotZ, targetZ, smoothing);
  }

  // Draw 3D model
  pushMatrix();
  translate(width/2, height/2, 0);

  // FIXED axis mapping for correct orientation
  rotateX(radians(rotY));  // Negative for correct pitch direction
  rotateY(radians(rotZ));   // Yaw maps to Y rotation
  rotateZ(radians(rotX));   // Roll maps to Z rotation

  scale(modelScale);

  if (modelLoaded && model != null) {
    fill(150, 200, 255);
    stroke(100);
    strokeWeight(0.5);
    shape(model);
  } else {
    drawFallbackDrone(2.0);
  }

  popMatrix();

  drawCoordinates();
  drawImprovedUI();
}

void loadModel() {
  try {
    println("🔄 Loading 3D model: " + modelFile);
    model = loadShape(modelFile);

    if (model != null) {
      modelLoaded = true;
      println("✅ Model loaded successfully!");

      // Center the model
      if (model.getWidth() != 0) {
        model.translate(-model.getWidth()/8, -model.getHeight()/4, -model.getDepth()/8);
      }

      println("📏 Using manual scale: " + modelScale);
    } else {
      println("❌ Failed to load model - using fallback drone");
      modelLoaded = false;
    }
  } catch (Exception e) {
    println("❌ Error loading model: " + e.getMessage());
    println("💡 Using fallback 3D drone shape");
    modelLoaded = false;
  }
}

void setupLighting() {
  ambientLight(80, 80, 90);
  directionalLight(200, 200, 180, -1, 0.5, -1);
  directionalLight(100, 100, 150, 1, -0.5, 0.5);
  directionalLight(120, 120, 80, 0, -1, 0.8);
}

void updateRotation() {
  if (serialConnected && !manualControl && !demoMode) {
    readSerialData();
  } else if (demoMode) {
    demoTime += 0.02;
    targetX = 30 * sin(demoTime);
    targetY = 45 * cos(demoTime * 0.7);
    targetZ = 60 * sin(demoTime * 0.3);
  } else if (manualControl) {
    targetY = map(mouseX, 0, width, -90, 90);
    targetX = map(mouseY, 0, height, -45, 45);
  }
}

void readSerialData() {
  if (myPort != null && myPort.available() > 0) {
    try {
      // Read all available data to prevent buffer buildup
      while (myPort.available() > 0) {
        String data = myPort.readStringUntil('\n');
        if (data != null) {
          data = trim(data);

          // Process the most recent data
          String[] values = split(data, ',');
          if (values.length >= 3) {
            // FIXED: Parse with error handling
            try {
              float newRoll = float(values[0]);
              float newPitch = float(values[1]); 
              float newYaw = float(values[2]);

              // Apply values immediately
              targetX = newRoll;
              targetY = newPitch;
              targetZ = newYaw;

              // Update debug info
              lastSerialTime = millis();
              serialDataCount++;

            } catch (NumberFormatException e) {
              // Skip malformed data
              println("⚠️ Bad data: " + data);
            }
          }
        }
      }
    } catch (Exception e) {
      println("Serial read error: " + e.getMessage());
    }
  }
}

void drawFallbackDrone(float size) {
  // Draw a simple drone shape when no model loaded
  stroke(255);
  strokeWeight(2);

  // Main body
  fill(100, 150, 200);
  box(size * 15, size * 5, size * 3);

  // Arms
  pushMatrix();
  fill(80, 120, 160);

  // Front arms
  translate(size * 8, 0, size * 8);
  box(size * 12, size * 2, size * 2);
  translate(0, 0, -size * 16);
  box(size * 12, size * 2, size * 2);

  // Props (simple circles)
  fill(200, 100, 100);
  translate(size * 8, 0, size * 16);
  sphere(size * 4);
  translate(-size * 16, 0, 0);
  sphere(size * 4);
  translate(0, 0, -size * 16);
  sphere(size * 4);
  translate(size * 16, 0, 0);
  sphere(size * 4);

  popMatrix();
}

void drawCoordinates() {
  pushMatrix();
  translate(100, height - 100, 0);
  strokeWeight(4);

  stroke(255, 0, 0);
  line(0, 0, 0, 50, 0, 0);
  fill(255, 0, 0);
  text("X", 55, 0);

  stroke(0, 255, 0);
  line(0, 0, 0, 0, -50, 0);
  fill(0, 255, 0);
  text("Y", 0, -55);

  stroke(0, 0, 255);
  line(0, 0, 0, 0, 0, 50);
  fill(0, 0, 255);
  text("Z", 0, 0);

  noStroke();
  popMatrix();
}

void drawImprovedUI() {
  // Main status panel
  fill(0, 0, 0, 200);
  rect(20, 20, 400, 280);

  fill(255);
  textSize(16);
  text("🎮 FIXED 3D Model Controller", 30, 45);

  textSize(12);
  text("Model: " + (modelLoaded ? "✅ " + modelFile : "❌ Fallback Drone"), 30, 65);
  text("Scale: " + nf(modelScale, 0, 2), 30, 80);

  text("Current Rotation:", 30, 105);
  text("Roll (X): " + nf(rotX, 0, 1) + "°", 30, 120);
  text("Pitch (Y): " + nf(rotY, 0, 1) + "°", 30, 135);  
  text("Yaw (Z): " + nf(rotZ, 0, 1) + "°", 30, 150);

  // Target values (what we're trying to reach)
  text("Target Rotation:", 30, 175);
  text("Target Roll: " + nf(targetX, 0, 1) + "°", 30, 190);
  text("Target Pitch: " + nf(targetY, 0, 1) + "°", 30, 205);
  text("Target Yaw: " + nf(targetZ, 0, 1) + "°", 30, 220);

  // Control mode
  text("Control Mode:", 30, 245);
  if (serialConnected && !manualControl && !demoMode) {
    fill(0, 255, 0);
    String mode = fastMode ? "📡 Serial IMU (FAST)" : "📡 Serial IMU (SMOOTH)";
    text(mode, 30, 260);
  } else if (demoMode) {
    fill(0, 150, 255);
    text("🎮 Demo Mode", 30, 260);
  } else if (manualControl) {
    fill(255, 150, 0);
    text("🖱️ Manual Control", 30, 260);
  } else {
    fill(255, 100, 100);
    text("⌨️ Keyboard Ready", 30, 260);
  }

  fill(255);
  textSize(10);
  text("F=Fast Mode | V=Debug | M=Manual | D=Demo | R=Reset | S=Serial", 30, 280);
  text("Fast Mode: " + (fastMode ? "ON (No Lag)" : "OFF (Smooth)"), 30, 295);

  // Serial debug panel
  if (showDebugValues && serialConnected) {
    fill(0, 0, 0, 200);
    rect(width - 300, 20, 280, 150);

    fill(255);
    textSize(14);
    text("🐛 Serial Debug", width - 290, 40);

    textSize(11);
    text("Data Rate: " + nf(serialDataCount / ((millis() - lastSerialTime + 1) / 1000.0), 0, 1) + " Hz", width - 290, 60);
    text("Last Update: " + nf((millis() - lastSerialTime) / 1000.0, 0, 2) + "s ago", width - 290, 75);

    text("Raw Values Received:", width - 290, 100);
    text("Roll: " + nf(targetX, 0, 2), width - 290, 115);
    text("Pitch: " + nf(targetY, 0, 2), width - 290, 130);
    text("Yaw: " + nf(targetZ, 0, 2), width - 290, 145);

    // Connection indicator
    if (millis() - lastSerialTime < 100) {
      fill(0, 255, 0);
      text("🟢 LIVE DATA", width - 290, 165);
    } else {
      fill(255, 0, 0);
      text("🔴 NO DATA", width - 290, 165);
    }
  }
}

void initSerial() {
  try {
    println("🔌 Available Serial Ports:");
    for (int i = 0; i < Serial.list().length; i++) {
      println("  " + i + ": " + Serial.list()[i]);
    }

    if (Serial.list().length > 0) {
      String portName = Serial.list()[0];
      myPort = new Serial(this, portName, 115200);
      myPort.bufferUntil('\n');
      serialConnected = true;
      println("📡 Connected to: " + portName);
    } else {
      println("❌ No serial ports found");
    }
  } catch (Exception e) {
    println("❌ Serial connection failed: " + e.getMessage());
    serialConnected = false;
  }
}

void keyPressed() {
  switch(key) {
    case 'r':
    case 'R':
      targetX = targetY = targetZ = 0;
      rotX = rotY = rotZ = 0;
      println("🔄 Reset orientation");
      break;

    case 'f':
    case 'F':
      fastMode = !fastMode;
      println("⚡ Fast mode: " + (fastMode ? "ON (No smoothing)" : "OFF (Smooth)"));
      break;

    case 'v':
    case 'V':
      showDebugValues = !showDebugValues;
      println("🐛 Debug values: " + (showDebugValues ? "ON" : "OFF"));
      break;

    case 'm':
    case 'M':
      manualControl = !manualControl;
      if (manualControl) demoMode = false;
      println("🖱️ Manual mode: " + (manualControl ? "ON" : "OFF"));
      break;

    case 'd':
    case 'D':
      demoMode = !demoMode;
      if (demoMode) manualControl = false;
      println("🎮 Demo mode: " + (demoMode ? "ON" : "OFF"));
      break;

    case 's':
    case 'S':
      if (serialConnected) {
        if (myPort != null) myPort.stop();
        serialConnected = false;
        println("📡 Serial disconnected");
      } else {
        initSerial();
      }
      break;

    case '+':
    case '=':
      modelScale += 5.0;
      println("📏 Scale: " + nf(modelScale, 0, 2));
      break;

    case '-':
    case '_':
      modelScale = max(5.0, modelScale - 5.0);
      println("📏 Scale: " + nf(modelScale, 0, 2));
      break;
  }

  // Arrow keys for manual rotation
  if (manualControl) {
    float step = 10.0;
    switch(keyCode) {
      case UP:    targetX -= step; break;
      case DOWN:  targetX += step; break;
      case LEFT:  targetZ -= step; break;
      case RIGHT: targetZ += step; break;
    }
  }
}

void mouseWheel(MouseEvent event) {
  float factor = event.getCount() > 0 ? 0.9 : 1.1;
  modelScale *= factor;
  modelScale = constrain(modelScale, 1.0, 200.0);
}

void serialEvent(Serial myPort) {
  // This function is automatically called when serial data arrives
  // The actual reading happens in readSerialData() for better control
}
