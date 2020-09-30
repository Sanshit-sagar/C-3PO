//
// Copyright 2016 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#import <AVFoundation/AVFoundation.h>

#import "ViewController.h"
#import "AudioController.h"
#import "SpeechRecognitionService.h"
#import "google/cloud/speech/v1/CloudSpeech.pbrpc.h"

#define SAMPLE_RATE 16000.0f

@interface ViewController () <AudioControllerDelegate, AVSpeechSynthesizerDelegate>
@property (nonatomic, strong) IBOutlet UITextView *textView;
@property (nonatomic, strong) NSMutableData *audioData;
@property (strong, nonatomic) AVSpeechSynthesizer *synthesizer;
@property (strong, nonatomic) AVAudioRecorder *recorder;
@end


UILabel *ready;
NSString *currentMood;
NSString *currentTone;
BOOL on;
BOOL shouldTranslate;
BOOL shouldTranslateFromEnglish;
BOOL isSpeaking;
NSString *language;
BOOL responseReceieved;
BOOL recordingForIdentification;
NSMutableDictionary *followUpInfo;
NSString *lastFile;
NSString *speakerProfile;
BOOL addressedSpeaker;
NSString *fabel;
BOOL introduceTime;
BOOL shouldReadFabel;
BOOL failedBefore;
UIImageView *imageViewLogo;


@implementation ViewController


- (void)viewDidLoad {
    
  [super viewDidLoad];

    fabel = @"A Hound, who in the days of his youth and strength had never yielded to any beast of the forest, encountered in his old age a boar in the chase. He seized him boldly by the ear, but could not retain his hold because of the decay of his teeth, so that the boar escaped. His master, quickly coming up, was very much disappointed, and fiercely abused the dog. The Hound looked up and said: 'It was not my fault, master; my spirit was as good as ever, but I could not help mine infirmities. I rather deserve to be praised for what I have been, than to be blamed for what I am.'";
    
    [AudioController sharedInstance].delegate = self;
    self.synthesizer = [[AVSpeechSynthesizer alloc] init];
    followUpInfo = [[NSMutableDictionary alloc] init];
    [self logInfo:@"\n"];
    [self logInfo:@"WELCOME TO C3PO! Select a mode to begin"];
    
    isSpeaking = FALSE;
    failedBefore = FALSE;
    responseReceieved = FALSE;
    _isReady.backgroundColor = [UIColor redColor];
    _isReady.textColor = [UIColor whiteColor];
    _isReady.layer.cornerRadius = 50;
    currentMood = @"relaxed";
    currentTone = @"silent";
    _moodLbl.backgroundColor = [UIColor blackColor];
    _moodLbl.textColor = [UIColor greenColor];
    _moodLbl.layer.cornerRadius = 50;
    _languageOutput.backgroundColor = self.view.backgroundColor;
    
    CGFloat screenWidth = [UIScreen mainScreen].bounds.size.width;
    CGFloat screenHeight = [[UIScreen mainScreen] bounds].size.height;
    imageViewLogo = [[UIImageView alloc] initWithFrame:CGRectMake(0.30*screenWidth, 0.05*screenHeight, 0.40*screenWidth, 0.12* screenHeight)];
    imageViewLogo.layer.cornerRadius = 10;
    imageViewLogo.clipsToBounds = true;
    NSString *ImageURLtouse = @"https://i.imgur.com/0Z6Pxmd.png";
    NSData *imageData = [NSData dataWithContentsOfURL:[NSURL URLWithString:ImageURLtouse]];
    imageViewLogo.image = [UIImage imageWithData:imageData];
    [self.view addSubview:imageViewLogo];
    //imageViewLogo.layer.cornerRadius = 30;
    //[ViewController addSubview:imageViewLogo];
}

- (NSString *) dateString
{
    NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
    formatter.dateFormat = @"ddMMMYY_hhmmssa";
    return [[formatter stringFromDate:[NSDate date]] stringByAppendingString:@".wav"];
}

- (void)removeFile:(NSString *)filename
{
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *documentsPath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0];
    NSString *filePath = [documentsPath stringByAppendingPathComponent:filename];
    NSError *error;
    BOOL success = [fileManager removeItemAtPath:filePath error:&error];
    if (success) { NSLog(@"removing old audio files...");}
    else {NSLog(@"Could not delete file -:%@ ",[error localizedDescription]);}
}


- (BOOL) record
{
    NSError *error;
    NSMutableDictionary *settings = [NSMutableDictionary dictionary];
    [settings setValue: [NSNumber numberWithInt:kAudioFormatLinearPCM] forKey:AVFormatIDKey];
    [settings setValue: [NSNumber numberWithFloat:16000] forKey:AVSampleRateKey];
    [settings setValue: [NSNumber numberWithInt: 1] forKey:AVNumberOfChannelsKey];
    [settings setValue: [NSNumber numberWithInt:16] forKey:AVLinearPCMBitDepthKey];
    [settings setValue: [NSNumber numberWithBool:NO] forKey:AVLinearPCMIsBigEndianKey];
    [settings setValue: [NSNumber numberWithBool:NO] forKey:AVLinearPCMIsFloatKey];
    [settings setValue:  [NSNumber numberWithInt: AVAudioQualityHigh] forKey:AVEncoderAudioQualityKey];
    
    NSArray *searchPaths =NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *documentPath_ = [searchPaths objectAtIndex: 0];
    NSString *pathToSave = [documentPath_ stringByAppendingPathComponent:[self dateString]];
    lastFile = pathToSave;
    NSURL *url = [NSURL fileURLWithPath:pathToSave];
    self.recorder = [[AVAudioRecorder alloc] initWithURL:url settings:settings error:&error];
    if (!self.recorder)
    {
        NSLog(@"Error establishing recorder: %@", error.localizedFailureReason);
        return NO;
    }
  
    self.recorder.meteringEnabled = YES;
    if (![self.recorder prepareToRecord])
    {
        NSLog(@"Error: Prepare to record failed");
        return NO;
    }
    
    if (![self.recorder record])
    {
        NSLog(@"Error: Record failed");
        return NO;
    }
    return YES;
}

- (void) stopRecording
{
    [self.recorder stop];
}

-(void)speechSynthesizer:(AVSpeechSynthesizer *)synthesizer didStartSpeechUtterance:(AVSpeechUtterance *)utterance {
    isSpeaking = TRUE;
    dispatch_async(dispatch_get_main_queue(), ^{
    });
}

-(void)speechSynthesizer:(AVSpeechSynthesizer *)synthesizer didFinishSpeechUtterance:(AVSpeechUtterance *)utterance {
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        if (introduceTime) {
            if (shouldReadFabel) {
            } else {
                [self logInfo:@"Time to introduce yourself."];
                [self introduceSelf];
            }
        } else {
            [self recordAudio:nil];
            if(failedBefore) {
                [self stopRecording];
          //      [self logInfo:@"STOPPED LISTENING"];
                return;
            }
          //  [self logInfo:@"Listening again..."];
        }
    });
}

-(void) introduceSelf {
    shouldReadFabel = true;
    [self stopRecording];
    [self talk:@"In order for me to really know and remember your voice, please read one of my favorite fabels as the words come accross the screen. It will only take a minute."];
    
    NSArray *fabelWords = [fabel componentsSeparatedByString:@" "];
    double delayInSeconds = 0.0;
    [self record];
    
    for (int i = 0; i < fabelWords.count - 2; i++) {
        
    
        delayInSeconds += 0.3;
        dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, (int64_t)(delayInSeconds * NSEC_PER_SEC));
        dispatch_after(popTime, dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^(void)
        {
            [self logInfo:[NSString stringWithFormat:@"%@ %@ %@", fabelWords[i], fabelWords[i+1], fabelWords[i+2]]];
            
            if (i == fabelWords.count - 3) {
                [self stopRecording];
                
                [self talk:@"Great. One moment while I learn your voice.."];
                
                [self enrollVoice:lastFile];
                
                
                [self talk:@"Thank you. Pleasure to meet you."];
                shouldReadFabel = false;
                introduceTime = false;
            }
        });
        
    }
    
   
}
-(void)fufillWithRequest:(NSString*)query {
    NSArray *followUps = [followUpInfo allKeys];
    NSLog(@"Follow ups: %@", followUps);
    if (followUps.count > 0) {
        NSString *escapedString = [[[query stringByReplacingOccurrencesOfString:@"+" withString:@"plus"] stringByReplacingOccurrencesOfString:@"-" withString:@"minus"] stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLHostAllowedCharacterSet]];
        NSString *escapedRequest = [[[followUpInfo[followUps[0]][@"request"] stringByReplacingOccurrencesOfString:@"+" withString:@"plus"] stringByReplacingOccurrencesOfString:@"-" withString:@"minus"] stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLHostAllowedCharacterSet]];
        
        NSString *escapedNeededFromBing = @"";
        NSLog(@"%@", followUpInfo[followUps[0]][@"needed_from_bing"]);
        for (NSString *required in followUpInfo[followUps[0]][@"needed_from_bing"]){
            if (required != [followUpInfo[followUps[0]][@"needed_from_bing"] lastObject]) {
                escapedNeededFromBing = [NSString stringWithFormat:@"%@%@,", escapedNeededFromBing, required];
            } else {
                escapedNeededFromBing = [NSString stringWithFormat:@"%@%@", escapedNeededFromBing, required];
            }
        }
        
        NSString *unescaped = [NSString stringWithFormat:@"https://evening-cove-60020.herokuapp.com/follow_up?identifier=ios&query=%@&intent=%@&needed_from_bing=%@&request=%@", escapedString, followUps[0], escapedNeededFromBing, escapedRequest];
        NSLog(@"FOLLOW UP REQUEST URL %@", unescaped);
        escapedString = unescaped;
        NSLog(@"ESCAPED STRING: %@", escapedString);
        NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:escapedString]];
        NSLog(@"%@", followUpInfo);
        //create the Method "GET" or "POST"
        NSError *error = nil;
        [urlRequest setHTTPMethod:@"POST"];
        
        if (@available(iOS 11.0, *)) {
//            NSData *d = [NSJSONSerialization dataWithJSONObject:followUpInfo[followUps[0]]
//                                                        options:NSJSONWritingSortedKeys
//                                                          error:&error];
            NSData* postData= [[NSString stringWithFormat:@"%@", followUpInfo[followUps[0]]] dataUsingEncoding:NSUTF8StringEncoding];
            [urlRequest setHTTPBody:postData];
        } else {
            // Fallback on earlier versions
        }
        //Convert the String to Data
        //Apply the data to the body
        NSURLSession *session = [NSURLSession sharedSession];
        NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
            NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
            if(httpResponse.statusCode == 200)
            {
                NSString *respString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                NSError *parseError = nil;
                NSDictionary *responseDictionary = [NSJSONSerialization JSONObjectWithData:[respString dataUsingEncoding:NSUTF8StringEncoding] options:0 error:&parseError];
                NSLog(@"The response is - %@. Error: %@",responseDictionary, parseError);
                if (1 == 2) {//([[responseDictionary valueForKey:@"i"] isEqualToString:@"IGNORE"]) {
                    
                } else {
                    
                    BOOL followUp = [[responseDictionary valueForKey:@"follow_up"] boolValue];
                    if (followUp) {
                        
                        [followUpInfo setObject:@{@"needed_from_bing":[responseDictionary objectForKey:@"needed_from_bing"], @"request":[responseDictionary valueForKey:@"request"]} forKey:[responseDictionary valueForKey:@"intent"]];
                        
                        
                        NSArray *responses = [responseDictionary objectForKey:@"result"];
                        if ([responses.lastObject isEqualToString:@"unsure"]) {
                            //isSpeaking = FALSE;
                            [self talk:@"I am really not sure what that means."];
                            return;
                        }
                        
                        NSLog(@"Responses: %@", responses);
                        currentMood =[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                        currentTone = [responseDictionary valueForKey:@"tone"];
                        //_moodLbl.text = [[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                        //NSLog(@"###****####Mood: %@",[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"]);
                        NSLog(@"The current tone is : %@", currentTone);
                        [self talk:responses.lastObject];
                        
                        
                        
                    } else {
                        for (NSString *key in followUpInfo.allKeys) {
                            [followUpInfo removeObjectForKey:key];
                        }
                        NSArray *responses = [responseDictionary objectForKey:@"result"];
                        if ([responses.lastObject isEqualToString:@"unsure"]) {
                            //isSpeaking = FALSE;
                            [self talk:@"I am really not sure what that means."];
                            currentTone = [responseDictionary valueForKey:@"tone"]; 
                            return;
                        }
                        
                        NSLog(@"Responses: %@", responses);
                        //MOOD LABEL SHOULD BE UPDATED HERE
                       // _moodLbl.text = [[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                         currentMood =[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                        currentTone = [responseDictionary valueForKey:@"tone"];
                        NSLog(@"The current tone is : %@", currentTone);
                        NSLog(@"###****####Mood: %@",[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"]);
                        if ([[responseDictionary valueForKey:@"intent"] isEqualToString:@"IntroduceMyself"]) {
                            introduceTime = true;
                        }
                        [self talk:responses.lastObject];
                    }
                }
                
            }
            else
            {
                isSpeaking = FALSE;
                [self recordAudio:nil];
                for (NSString *key in followUpInfo.allKeys) {
                    [followUpInfo removeObjectForKey:key];
                }
                dispatch_async(dispatch_get_main_queue(), ^{
//                    self.statusLbl.text = @"Error.";
                });
            }
        }];
        [dataTask resume];
    }
    //NO FOLLOWUP NEEDED
    else {
        NSString *escapedString = [[[query stringByReplacingOccurrencesOfString:@"+" withString:@"plus"] stringByReplacingOccurrencesOfString:@"-" withString:@"minus"] stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLHostAllowedCharacterSet]];
    
        NSString *unescaped = [NSString stringWithFormat:@"https://evening-cove-60020.herokuapp.com/payload?identifier=ios&query=%@&language=%@&voice_id=%@", escapedString, [language componentsSeparatedByString:@"-"][0], speakerProfile];
        NSLog(@"Unescaped: %@", unescaped);
        escapedString = unescaped;
        NSLog(@"ESCAPED STRING: %@", escapedString);
        NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:escapedString]];
        
        //create the Method "GET" or "POST"
        [urlRequest setHTTPMethod:@"POST"];
        //Convert the String to Data
        //Apply the data to the body
        NSURLSession *session = [NSURLSession sharedSession];
        NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
            NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
            if(httpResponse.statusCode == 200)
            {
                NSString *respString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                NSError *parseError = nil;
                NSDictionary *responseDictionary = [NSJSONSerialization JSONObjectWithData:[respString dataUsingEncoding:NSUTF8StringEncoding] options:0 error:&parseError];
                
                if ([responseDictionary objectForKey:@"language"])
                {
                     dispatch_async(dispatch_get_main_queue(), ^{
                         self.languageOutput.text = [responseDictionary objectForKey:@"language"];
                         language =  [responseDictionary objectForKey:@"language"];
                     });
                }
                
                NSLog(@"The response is - %@. Error: %@",responseDictionary, parseError);
                if (1 == 2) {
                    //THIS IF STATEMENT WILL NEVER GET HIT
                    //([[responseDictionary valueForKey:@"i"] isEqualToString:@"IGNORE"]) {
                    }
                else {
                    BOOL followUp = [[responseDictionary valueForKey:@"follow_up"] boolValue];
                    if (followUp)
                    {
                        NSLog(@"FOLLOW UP FEQWUIER 1ST TRY");
                        //                    NSArray *array = [responseDictionary objectForKey:@"needs"];
                        //                    NSLog([responseDictionary valueForKey:@"response"]);
                        [followUpInfo setObject:@{@"needed_from_bing":[responseDictionary objectForKey:@"needed_from_bing"], @"request":[responseDictionary valueForKey:@"request"]} forKey:[responseDictionary valueForKey:@"intent"]];
                        NSArray *responses = [responseDictionary objectForKey:@"result"];
                        if ([responses.lastObject isEqualToString:@"unsure"])
                        {
                            //isSpeaking = FALSE;
                            [self talk:@"I am really not sure what that means."];
                            return;
                        }
                        NSLog(@"Responses: %@", responses);
                       // _moodLbl.text = [[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                         currentMood =[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                        currentTone = [responseDictionary valueForKey:@"tone"];
                        NSLog(@"The current tone is : %@", currentTone);
                       // NSLog(@"Mood: %@",[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"]);
                        [self talk:responses.lastObject];
                    }
                else {
                        for (NSString *key in followUpInfo.allKeys)
                        {
                            [followUpInfo removeObjectForKey:key];
                        }
                        NSArray *responses = [responseDictionary objectForKey:@"result"];
                        if ([responses.lastObject isEqualToString:@"unsure"])
                        {
                            //isSpeaking = FALSE;
                            [self talk:@"I am really not sure what that means."];
                            return;
                        }
                        
                        NSLog(@"Responses: %@", responses);
                        currentMood =[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                        currentTone = [responseDictionary valueForKey:@"tone"];
                    NSLog(@"The current tone is : %@", currentTone);
                        NSLog(@"###****####Mood: %@",[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"]);
                        [self talk:responses.lastObject];
                        //                  for (NSString *response in responses) {
                        //                        [self talk:response];
                        //                    }
                        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                        //NSLog(@"On to second..");
                        });
                        [self talk:[responseDictionary valueForKey:@"response"]];
                    }
                }
                
            }
            else
            {
                //isSpeaking = FALSE;
                [self talk:@"The server is not online right now"];
                _isReady.backgroundColor = [UIColor redColor];
                _isReady.text = @"NOT LISTENING";
                on = FALSE;
                [self stopAudio:nil];
                
               // [self recordAudio:nil];
                for (NSString *key in followUpInfo.allKeys) {
                    [followUpInfo removeObjectForKey:key];
                }
                dispatch_async(dispatch_get_main_queue(), ^{
                //self.statusLbl.text = @"Error.";
                });
                NSLog(@"Error %@", error );
            }
        }];
        [dataTask resume];
        
    }
}




- (IBAction)recordAudio:(id)sender {
  AVAudioSession *audioSession = [AVAudioSession sharedInstance];
  [audioSession setCategory:AVAudioSessionCategoryPlayAndRecord error:nil];
  _audioData = [[NSMutableData alloc] init];
  [[AudioController sharedInstance] prepareWithSampleRate:SAMPLE_RATE];
  [[SpeechRecognitionService sharedInstance] setSampleRate:SAMPLE_RATE];
    if(shouldTranslateFromEnglish) {
        [[SpeechRecognitionService sharedInstance] setLang:@"en-US"];
    }
    else {
        [[SpeechRecognitionService sharedInstance] setLang:language];
    }
  [[AudioController sharedInstance] start];
}

- (IBAction)stopAudio:(id)sender {
  [[AudioController sharedInstance] stop];
  [[SpeechRecognitionService sharedInstance] stopStreaming];
}

- (void) processSampleData:(NSData *)data
{
  [self.audioData appendData:data];
  NSInteger frameCount = [data length] / 2;
  int16_t *samples = (int16_t *) [data bytes];
  int64_t sum = 0;
  for (int i = 0; i < frameCount; i++) {
    sum += abs(samples[i]);
}

  int chunk_size = 0.1 * SAMPLE_RATE * 2;

  if ([self.audioData length] > chunk_size) {
      if (recordingForIdentification) {}
      else {}
      
    [[SpeechRecognitionService sharedInstance] streamAudioData:self.audioData
                                                withCompletion:^(StreamingRecognizeResponse *response, NSError *error)
      {
          if (error)
          {
              if(failedBefore) {
                  [self stopAudio:nil];
                  _isReady.backgroundColor = [UIColor redColor];
                  on = FALSE;
                  return;
              }
              failedBefore = TRUE;
              [self logInfo:[error localizedDescription]];
              [[AudioController sharedInstance] stop];
              [[SpeechRecognitionService sharedInstance] stopStreaming];
              [self stopRecording];
              [self talk:@"Looks like my servers aren't online right now. Select a mode to try again."];
              [self logInfo:@"restarting..."];
          }
          else if (response)
          {
            failedBefore = false;
            BOOL finished = NO;
            if (recordingForIdentification) {}
            else {recordingForIdentification = true;}
            for (StreamingRecognitionResult *result in response.resultsArray)
            { if (result.isFinal) { finished = YES; } }
            if (finished) {
                StreamingRecognitionResult *result_array_object = response.resultsArray[0];
                NSString *userQuery = result_array_object.alternativesArray[0].transcript;
                float confidence = result_array_object.alternativesArray[0].confidence;
                [self stopRecording];
                if (shouldTranslate) {
                    [self translateText:userQuery];
                }
                else if (shouldTranslateFromEnglish) {
                    [self translateTextFromEnglish:userQuery];
                }
                else {
                    [self fufillWithRequest:userQuery];
                }
                NSLog(@"Audio File: %@", lastFile);
                [self stopAudio:nil];
                [self logInfo:[NSString stringWithFormat:@"QUERY: %@", userQuery]];
                [self logInfo:[NSString stringWithFormat:@"CONFIDENCE: %f", confidence]];
                _isReady.backgroundColor = [UIColor redColor];
                _isReady.text = @"NOT LISTENING";
            }
          }
        }
     ];
    self.audioData = [[NSMutableData alloc] init];
    _isReady.backgroundColor = [UIColor greenColor];
    _isReady.text = @"LISTENING";
  }
}

-(IBAction)translate:(id)sender {
    NSInteger selectedIndex = self.segmentControl.selectedSegmentIndex;
    NSLog(@"selected index: %ld", (long)selectedIndex);
    if (selectedIndex == 0) {
        language = @"en-US";
        _currentLanguage.text = @"English";
    } else if (selectedIndex == 1) {
        language = @"zh-CN";
        _currentLanguage.text = @"Mandarin";
    } else if (selectedIndex == 2) {
        language = @"ar-PS";
        _currentLanguage.text = @"Arabic";
    } else if (selectedIndex == 3) {
        language = @"th-TH";
        _currentLanguage.text = @"Thai";
    } else if (selectedIndex == 4) {
        language = @"ja-JP";
        _currentLanguage.text = @"Japanese";
    } else if (selectedIndex == 5) {
        language = @"hi-IN";
        _currentLanguage.text = @"Hindi";
    } else if (selectedIndex == 6) {
        language = @"es-ES";
        _currentLanguage.text = @"Spanish";
    } else if (selectedIndex == 7) {
        language = @"fr-FR";
        _currentLanguage.text = @"French";
    }
    
    if (on) {
        on = false;
        shouldTranslate = FALSE;
        shouldTranslateFromEnglish = FALSE;
        [self stopAudio:nil];
        [self logInfo:@"STOPPED LISTENING"];
        _isReady.backgroundColor = [UIColor redColor];
        _isReady.text = @"NOT LISTENING";
    } else {
        on = true;
        shouldTranslate = TRUE;
        shouldTranslateFromEnglish = FALSE;
        [self recordAudio:nil];
        [self logInfo:@"STARTED LISTENING"];
        _isReady.backgroundColor = [UIColor greenColor];
        ready.backgroundColor = [UIColor greenColor];
        _isReady.text = @"LISTENING";
    }
}

-(IBAction)translateFromEnglish:(id)sender {
    NSInteger selectedIndex = self.segmentControl.selectedSegmentIndex;
    NSLog(@"selected index: %ld", (long)selectedIndex);
    if (selectedIndex == 0) {
        language = @"en-US";
        _currentLanguage.text = @"English";
    } else if (selectedIndex == 1) {
        language = @"zh-CN";
        _currentLanguage.text = @"Mandarin";
    } else if (selectedIndex == 2) {
        language = @"ar-PS";
        _currentLanguage.text = @"Arabic";
    } else if (selectedIndex == 3) {
        language = @"th-TH";
        _currentLanguage.text = @"Thai";
    } else if (selectedIndex == 4) {
        language = @"ja-JP";
        _currentLanguage.text = @"Japanese";
    } else if (selectedIndex == 5) {
        language = @"hi-IN";
        _currentLanguage.text = @"Hindi";
    } else if (selectedIndex == 6) {
        language = @"es-ES";
        _currentLanguage.text = @"Spanish";
    } else if (selectedIndex == 7) {
        language = @"fr-FR";
        _currentLanguage.text = @"French";
    }
    
    if (on) {
        on = false;
        shouldTranslate = FALSE;
        shouldTranslateFromEnglish = FALSE;
        [self stopAudio:nil];
        [self logInfo:@"STOPPED LISTENING"];
        _isReady.backgroundColor = [UIColor redColor];
        _isReady.text = @"NOT LISTENING";
    } else {
        on = true;
        shouldTranslate = FALSE;
        shouldTranslateFromEnglish = TRUE;
        [self recordAudio:nil];
        [self logInfo:@"STARTED LISTENING"];
        _isReady.backgroundColor = [UIColor greenColor];
        ready.backgroundColor = [UIColor greenColor];
        _isReady.text = @"LISTENING";
    }
}


-(void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    [self.languageOutput resignFirstResponder];
}

-(IBAction)normalSpeech:(id)sender {
    NSInteger selectedIndex = self.segmentControl.selectedSegmentIndex;
    NSLog(@"selected index: %ld", (long)selectedIndex);
    if (selectedIndex == 0) {
        language = @"en-US";
        _currentLanguage.text = @"English";
    } else if (selectedIndex == 1) {
        language = @"zh-CN";
        _currentLanguage.text = @"Mandarin";
    } else if (selectedIndex == 2) {
        language = @"ar-PS";
        _currentLanguage.text = @"Arabic";
    } else if (selectedIndex == 3) {
        language = @"th-TH";
        _currentLanguage.text = @"Thai";
    } else if (selectedIndex == 4) {
        language = @"ja-JP";
        _currentLanguage.text = @"Japanese";
    } else if (selectedIndex == 5) {
        language = @"hi-IN";
        _currentLanguage.text = @"Hindi";
    } else if (selectedIndex == 6) {
        language = @"es-ES";
        _currentLanguage.text = @"Spanish";
    } else if (selectedIndex == 7) {
        language = @"fr-FR";
        _currentLanguage.text = @"French";
    }
    
    if (on) {
        on = false;
        shouldTranslate = FALSE;
        shouldTranslateFromEnglish = FALSE;
        [self stopAudio:nil];
        [self logInfo:@"STOPPED LISTENING"];
        _isReady.backgroundColor = [UIColor redColor];
        _isReady.text = @"NOT LISTENING";
    } else {
        on = true;
        shouldTranslate = FALSE;
        shouldTranslateFromEnglish = FALSE;
        [self recordAudio:nil];
        [self logInfo:@"STARTED LISTENING"];
        _isReady.backgroundColor = [UIColor greenColor];
        _isReady.text = @"LISTENING";
    }
}


-(void) translateText:(NSString *)text {
    NSString *escapedString = [[[text stringByReplacingOccurrencesOfString:@"+" withString:@"plus"] stringByReplacingOccurrencesOfString:@"-" withString:@"minus"] stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLHostAllowedCharacterSet]];
    NSString *to_language = [language componentsSeparatedByString:@"-"][0];
    NSString *unescaped = [NSString stringWithFormat:@"https://evening-cove-60020.herokuapp.com/translate?query=%@&to_language=%@", escapedString, to_language];
    escapedString = unescaped;
    
    NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:escapedString]];
    [urlRequest setHTTPMethod:@"POST"];
    NSURLSession *session = [NSURLSession sharedSession];
    NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
        if(httpResponse.statusCode == 200)
        {
            NSString *respString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            NSError *parseError = nil;
            NSDictionary *responseDictionary = [NSJSONSerialization JSONObjectWithData:[respString dataUsingEncoding:NSUTF8StringEncoding] options:0 error:&parseError];
        
                    for (NSString *key in followUpInfo.allKeys) {
                        [followUpInfo removeObjectForKey:key];
                    }
                    NSArray *responses = [responseDictionary objectForKey:@"result"];
                    if ([responses.lastObject isEqualToString:@"unsure"]) {
                        //isSpeaking = FALSE;
                        [self talk:@"I am really not sure what that means."];
                        return;
                    }
                    
                    NSLog(@"Responses: %@", responses);
                    _moodLbl.text = @"translating...";
            //[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"];
                   // NSLog(@"Mood: %@",[[responseDictionary valueForKey:@"mood"] valueForKey:@"mood"]);
                    
                    [self talk:responses.lastObject];
                    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                        NSLog(@"On to second..");
                    });
        }

        else
        {
            isSpeaking = FALSE;
            [self recordAudio:nil];
            for (NSString *key in followUpInfo.allKeys) {
                [followUpInfo removeObjectForKey:key];
            }
            dispatch_async(dispatch_get_main_queue(), ^{
//                self.statusLbl.text = @"Error.";
            });
            NSLog(@"Error %@", error );
        }
    }];
    [dataTask resume];
}


-(void) translateTextFromEnglish:(NSString *)text {
    NSLog(@"Everything works so far in the translate from english function"); 
    //[self talk:@"YUP YUP YUP IT WORKS"];
    NSString *escapedString = [[[text stringByReplacingOccurrencesOfString:@"+" withString:@"plus"] stringByReplacingOccurrencesOfString:@"-" withString:@"minus"] stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLHostAllowedCharacterSet]];
    NSString *to_language = [language componentsSeparatedByString:@"-"][0];
    NSString *unescaped = [NSString stringWithFormat:@"https://evening-cove-60020.herokuapp.com/translateReversed?query=%@&to_language=%@", escapedString, to_language];
    escapedString = unescaped;
    
    NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:escapedString]];
    [urlRequest setHTTPMethod:@"POST"];
    NSURLSession *session = [NSURLSession sharedSession];
    NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
        if(httpResponse.statusCode == 200)
        {
            NSString *respString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            NSError *parseError = nil;
            NSDictionary *responseDictionary = [NSJSONSerialization JSONObjectWithData:[respString dataUsingEncoding:NSUTF8StringEncoding] options:0 error:&parseError];
            
            for (NSString *key in followUpInfo.allKeys) {
                [followUpInfo removeObjectForKey:key];
            }
            NSArray *responses = [responseDictionary objectForKey:@"result"];
            if ([responses.lastObject isEqualToString:@"unsure"]) {
                //isSpeaking = FALSE;
                [self talk:@"I am really not sure what that means."];
                return;
            }
            
            NSLog(@"Responses: %@", responses);
            _moodLbl.text = @"translating...";
           
            [self talk:responses.lastObject];
            dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                NSLog(@"On to second..");
            });
        }
        
        else
        {
            isSpeaking = FALSE;
            [self recordAudio:nil];
            for (NSString *key in followUpInfo.allKeys) {
                [followUpInfo removeObjectForKey:key];
            }
            dispatch_async(dispatch_get_main_queue(), ^{
                //                self.statusLbl.text = @"Error.";
            });
            NSLog(@"Error %@", error );
        }
    }];
    [dataTask resume];
}

-(void) meetNewPerson {
    
    speakerProfile = @"";
    [self talk:@"Wait, first, I do not believe we have met before. What is your name?"];
    
    
}

-(void)talk:(NSString*)str{
    if (str == nil) {
        return;
    }
    [self stopAudio:nil];
    NSLog(@"About to talk to identifier: %@", speakerProfile);
    NSLog(@"SAYING: %@", str);
    dispatch_async(dispatch_get_main_queue(), ^{
            [self logInfo:str];
        });
    [self setAudioOutputSpeaker:true];
    addressedSpeaker = true;
    dispatch_async(dispatch_get_main_queue(), ^{
        AVSpeechUtterance *utterance = [[AVSpeechUtterance alloc] initWithString:str];
        NSString *to_language;
        if(shouldTranslate) {to_language = @"en";}
        else { to_language = [language componentsSeparatedByString:@"-"][0]; }
        if(shouldTranslateFromEnglish==FALSE && [language isEqualToString:@"en"]) {
            utterance.voice = [AVSpeechSynthesisVoice voiceWithIdentifier:AVSpeechSynthesisVoiceIdentifierAlex];
        }
        else {
            utterance.voice = [AVSpeechSynthesisVoice voiceWithLanguage:to_language];
        }
        self.synthesizer.delegate = self;
        
        [self.synthesizer speakUtterance:utterance];
    });
}


- (void)setAudioOutputSpeaker:(BOOL)enabled
{
    AVAudioSession *session = [AVAudioSession sharedInstance];
    BOOL success;
    NSError* error;
    
    success =[session setCategory:AVAudioSessionCategoryPlayback withOptions:AVAudioSessionCategoryOptionDuckOthers error:&error];
    
//    success = [session overrideOutputAudioPort:AVAudioSessionPortOverrideSpeaker error:&error];
    
    if (!success)  NSLog(@"AVAudioSession error setting category:%@",[error localizedDescription]);
    
}

-(void) logInfo:(NSString *)text {
    
    NSLog(@"%@", text);
    dispatch_async(dispatch_get_main_queue(), ^{
        _moodLbl.text = currentMood;
        _toneLbl.text = currentTone; 
         [_textView setText:[NSString stringWithFormat:@"%@ \n %@", _textView.text, text]];
        [_textView scrollRangeToVisible:NSMakeRange(_textView.text.length-1, 0)];
        
    });
}

-(void)checkVoice:(NSString *)filename completion:  (void (^)(void)) completion {
    
    
    
    
    NSString *path = [[NSURL URLWithString:lastFile] path];
    NSData *buffer = [[NSFileManager defaultManager] contentsAtPath:path];
    
    

    [self removeFile:filename];
    
    
    NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:@""]];
    
    //    NSString *userUpdate =[NSString stringWithFormat:@"identificationProfileIds=(3D18DF4E-9B09-47A6-A790-58335E085BF0)&entities=true&shortAudio=true"];
    
    //create the Method "GET" or "POST"
    [urlRequest setHTTPMethod:@"POST"];
    [urlRequest setValue:@"multipart/form-data" forHTTPHeaderField:@"Content-Type"];
    [urlRequest setValue:@"" forHTTPHeaderField:@"Ocp-Apim-Subscription-Key"];
    //Convert the String to Data
    
  
    [urlRequest setHTTPBody:buffer];
//    [urlRequest setHTTPBody:buffer];
    
    NSURLSession *session = [NSURLSession sharedSession];
    NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
        
        NSLog(@"Fetched inital request with status code: %li", (long)httpResponse.statusCode);
        NSString* dataString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
        NSLog(@"data string: %@", dataString);
        if (httpResponse.statusCode == 202) {
            
            //checking status of identification
            NSString *operationCheck = [httpResponse.allHeaderFields valueForKey:@"Operation-Location"];
            
            NSMutableURLRequest *urlRequest = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:operationCheck]];
        
            [urlRequest setHTTPMethod:@"GET"];
            
            [urlRequest setValue:@"" forHTTPHeaderField:@"Ocp-Apim-Subscription-Key"];
            
            
            for (int i = 0; i < 40; i++) {
                
                dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                    
                
                    NSURLSession *session = [NSURLSession sharedSession];
                    NSURLSessionDataTask *dataTask = [session dataTaskWithRequest:urlRequest completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
                        NSHTTPURLResponse *httpResponse = (NSHTTPURLResponse *)response;
                        NSString* dataString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                        NSLog(@"data string: %@", dataString);
                        if(httpResponse.statusCode == 200)
                        {
                            NSError *parseError = nil;
                            NSDictionary *responseDictionary = [NSJSONSerialization JSONObjectWithData:data options:0 error:&parseError];
                            NSLog(@"The response is - %@",responseDictionary);
                            NSString *status = [responseDictionary valueForKey:@"status"];
                            if ([status isEqualToString:@"succeeded"]) {
                                
                                //Got response from identity checker
                                if ([[responseDictionary objectForKey:@"processingResult"] valueForKey:@"identifiedProfileId"] == speakerProfile) {
                                    
                                } else {
                                    addressedSpeaker = false;
                                }
                                speakerProfile = [[responseDictionary objectForKey:@"processingResult"] valueForKey:@"identifiedProfileId"];
                                
                                if (completion != nil)
                                {
                                    //The data task's completion block runs on a background thread
                                    //by default, so invoke the completion handler on the main thread
                                    //for safety
                                    dispatch_async(dispatch_get_main_queue(), completion);
                                }
                                
                            } else if ([status isEqualToString:@"running"]) {
                                //waiting for voice check to be done
                                NSLog(@"voice check in progress");
                                
                            } else {
                                
                                speakerProfile = @"00000000-0000-0000-0000-000000000000";
                                if (completion != nil)
                                {
                                    //The data task's completion block runs on a background thread
                                    //by default, so invoke the completion handler on the main thread
                                    //for safety
                                    dispatch_async(dispatch_get_main_queue(), completion);
                                }
                            }
                            
                        }
                        else
                        {
                            NSLog(@"Error");
                            if (completion != nil)
                            {
                                //The data task's completion block runs on a background thread
                                //by default, so invoke the completion handler on the main thread
                                //for safety
                                dispatch_async(dispatch_get_main_queue(), completion);
                            }
                            
                        }
                    }];
                    [dataTask resume];
                });
            }
            
        }
        
    }];
    NSLog(@"Done getting voice. %@", speakerProfile);
    [dataTask resume];
    return;
}

-(void)enrollVoice:(NSString *)filename {
    NSLog(@"%@", filename);
    NSString *pathData = [[NSURL URLWithString:lastFile] path];
    NSData *buffer = [[NSFileManager defaultManager] contentsAtPath:pathData];
    
    NSLog(@"%@", buffer);
    
    NSString* path = @"";
    NSArray* array = @[
                       // Request parameters
                       @"entities=true",
                       @"shortAudio=true",
                       ];
    
    NSString* string = [array componentsJoinedByString:@"&"];
    path = [path stringByAppendingFormat:@"?%@", string];
    
    NSLog(@"%@", path);
    
    NSMutableURLRequest* _request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:path]];
    [_request setHTTPMethod:@"POST"];
    // Request headers
    [_request setValue:@"multipart/form-data" forHTTPHeaderField:@"Content-Type"];
    [_request setValue:@"" forHTTPHeaderField:@"Ocp-Apim-Subscription-Key"];
    // Request body
    [_request setHTTPBody:buffer];
    
    //    [_request setHTTPBody:buffer dataUsingEncoding:NSUTF8StringEncoding]];
    
    NSURLResponse *response = nil;
    NSError *error = nil;
    NSData* _connectionData = [NSURLConnection sendSynchronousRequest:_request returningResponse:&response error:&error];
    
    
    if (nil != error)
    {
        NSLog(@"Error: %@", error);
    }
    else
    {
        NSError* error = nil;
        NSMutableDictionary* json = nil;
        NSString* dataString = [[NSString alloc] initWithData:_connectionData encoding:NSUTF8StringEncoding];
        NSLog(@"%@", dataString);
        
        
        
        if (nil != _connectionData)
        {
            json = [NSJSONSerialization JSONObjectWithData:_connectionData options:NSJSONReadingMutableContainers error:&error];
        }
        
        if (error || !json)
        {
            NSLog(@"Could not parse loaded json with error:%@", error);
        }
        
        NSLog(@"%@", json);
        _connectionData = nil;
    }
    
    [self removeFile:filename];
    
    
    
    
    
}


@end

/*
 Arabic (Saudi Arabia) - ar-SA
 Chinese (China) - zh-CN
 Chinese (Hong Kong SAR China) - zh-HK
 Chinese (Taiwan) - zh-TW
 Czech (Czech Republic) - cs-CZ
 Danish (Denmark) - da-DK
 Dutch (Belgium) - nl-BE
 Dutch (Netherlands) - nl-NL
 English (Australia) - en-AU
 English (Ireland) - en-IE
 English (South Africa) - en-ZA
 English (United Kingdom) - en-GB
 English (United States) - en-US
 Finnish (Finland) - fi-FI
 French (Canada) - fr-CA
 French (France) - fr-FR
 German (Germany) - de-DE
 Greek (Greece) - el-GR
 Hebrew (Israel) - he-IL
 Hindi (India) - hi-IN
 Hungarian (Hungary) - hu-HU
 Indonesian (Indonesia) - id-ID
 Italian (Italy) - it-IT
 Japanese (Japan) - ja-JP
 Korean (South Korea) - ko-KR
 Norwegian (Norway) - no-NO
 Polish (Poland) - pl-PL
 Portuguese (Brazil) - pt-BR
 Portuguese (Portugal) - pt-PT
 Romanian (Romania) - ro-RO
 Russian (Russia) - ru-RU
 Slovak (Slovakia) - sk-SK
 Spanish (Mexico) - es-MX
 Spanish (Spain) - es-ES
 Swedish (Sweden) - sv-SE
 Thai (Thailand) - th-TH
 Turkish (Turkey) - tr-TR
 */

