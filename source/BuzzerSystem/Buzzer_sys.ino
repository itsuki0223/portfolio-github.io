int sens = 300;//5mS
int sensor_value[300];//value of sens
float value;
int num = 0;

bool Buzzer = false;
bool Button = false;
bool Sound = true;
int count = 0;
int interval = 50;//10mS
int stop_time = 300;//10ms

int buzzer = 16;
int button = 13;
int light = 12;

void setup() {
  Serial.begin(9600);
  pinMode(buzzer,OUTPUT);
  pinMode(button,INPUT);
  pinMode(light,INPUT);
}

void loop() {
  //light
  if(num >= sens){
    num = 0;
  }
  sensor_value[num] = digitalRead(light);
  for(int i = 0; i < sens; i++){
    value += sensor_value[i]; 
  }
  value = value / sens;
  num++;
  //Serial.println(value);
  
  if(value >= 0.5){
    Buzzer = true;
  }else{
    Buzzer = false;
    Button = false;
  }

  //button
//  if(digitalRead(button) == 1){
//    Button = true;
//  }
//    Serial.println(digitalRead(button));

  //buzzer
  if(Buzzer == true and Button == false){
    //Serial.println("ok");
    if(Sound == true and count % interval == 0){
      digitalWrite(buzzer,HIGH);
      Sound = false;
    }else if(Sound == false and count % interval == 0){
      digitalWrite(buzzer,LOW);
      Sound = true;
    }
    if (count > stop_time){
      Button = true;
    }
    count++;
  }else{
    digitalWrite(buzzer,LOW);
    count = 0;
  }
  
  delay(10);
}
