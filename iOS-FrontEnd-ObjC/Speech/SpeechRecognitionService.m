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

#import "SpeechRecognitionService.h"

#import <GRPCClient/GRPCCall.h>
#import <RxLibrary/GRXBufferedPipe.h>
#import <ProtoRPC/ProtoRPC.h>

@interface SpeechRecognitionService ()

@property (nonatomic, assign) BOOL streaming;
@property (nonatomic, strong) Speech *client;
@property (nonatomic, strong) GRXBufferedPipe *writer;
@property (nonatomic, strong) GRPCProtoCall *call;

@end

@implementation SpeechRecognitionService

+ (instancetype) sharedInstance {
  static SpeechRecognitionService *instance = nil;
  if (!instance) {
    instance = [[self alloc] init];
    instance.lang = @"en-US";
    instance.sampleRate = 16000.0; // default value
  }
  return instance;
}

- (void) streamAudioData:(NSData *) audioData
          withCompletion:(SpeechRecognitionCompletionHandler)completion {

  if (!_streaming) {
    // if we aren't already streaming, set up a gRPC connection
    _client = [[Speech alloc] initWithHost:HOST];
    _writer = [[GRXBufferedPipe alloc] init];
    _call = [_client RPCToStreamingRecognizeWithRequestsWriter:_writer
                                         eventHandler:^(BOOL done, StreamingRecognizeResponse *response, NSError *error) {
                                           completion(response, error);
                                         }];

    // authenticate using an API key obtained from the Google Cloud Console
    _call.requestHeaders[@"X-Goog-Api-Key"] = API_KEY;
    // if the API key has a bundle ID restriction, specify the bundle ID like this
    _call.requestHeaders[@"X-Ios-Bundle-Identifier"] = [[NSBundle mainBundle] bundleIdentifier];

    NSLog(@"HEADERS: %@", _call.requestHeaders);

    [_call start];
    _streaming = YES;

    // send an initial request message to configure the service
    RecognitionConfig *recognitionConfig = [RecognitionConfig message];
    recognitionConfig.encoding = RecognitionConfig_AudioEncoding_Linear16;
    recognitionConfig.sampleRateHertz = self.sampleRate;
      recognitionConfig.languageCode = self.lang;//@"th-Th";//@"id-ID";
    recognitionConfig.maxAlternatives = 30;

    StreamingRecognitionConfig *streamingRecognitionConfig = [StreamingRecognitionConfig message];
    streamingRecognitionConfig.config = recognitionConfig;
    streamingRecognitionConfig.singleUtterance = NO;
    streamingRecognitionConfig.interimResults = YES;

    StreamingRecognizeRequest *streamingRecognizeRequest = [StreamingRecognizeRequest message];
    streamingRecognizeRequest.streamingConfig = streamingRecognitionConfig;

    [_writer writeValue:streamingRecognizeRequest];
  }

  // send a request message containing the audio data
  StreamingRecognizeRequest *streamingRecognizeRequest = [StreamingRecognizeRequest message];
  streamingRecognizeRequest.audioContent = audioData;
  [_writer writeValue:streamingRecognizeRequest];
}

- (void) stopStreaming {
  if (!_streaming) {
    return;
  }
  [_writer finishWithError:nil];
  _streaming = NO;
}

- (BOOL) isStreaming {
  return _streaming;
}
/*
 Afrikaans (Suid-Afrika)    af-ZA    Afrikaans (South Africa)
 አማርኛ (ኢትዮጵያ)    am-ET    Amharic (Ethiopia)
 Հայ (Հայաստան)    hy-AM    Armenian (Armenia)
 Azərbaycan (Azərbaycan)    az-AZ    Azerbaijani (Azerbaijan)
 Bahasa Indonesia (Indonesia)    id-ID    Indonesian (Indonesia)
 Bahasa Melayu (Malaysia)    ms-MY    Malay (Malaysia)
 বাংলা (বাংলাদেশ)    bn-BD    Bengali (Bangladesh)
 বাংলা (ভারত)    bn-IN    Bengali (India)
 Català (Espanya)    ca-ES    Catalan (Spain)
 Čeština (Česká republika)    cs-CZ    Czech (Czech Republic)
 Dansk (Danmark)    da-DK    Danish (Denmark)
 Deutsch (Deutschland)    de-DE    German (Germany)
 English (Australia)    en-AU    English (Australia)
 English (Canada)    en-CA    English (Canada)
 English (Ghana)    en-GH    English (Ghana)
 English (Great Britain)    en-GB    English (United Kingdom)
 English (India)    en-IN    English (India)
 English (Ireland)    en-IE    English (Ireland)
 English (Kenya)    en-KE    English (Kenya)
 English (New Zealand)    en-NZ    English (New Zealand)
 English (Nigeria)    en-NG    English (Nigeria)
 English (Philippines)    en-PH    English (Philippines)
 English (South Africa)    en-ZA    English (South Africa)
 English (Tanzania)    en-TZ    English (Tanzania)
 English (United States)    en-US    English (United States)
 Español (Argentina)    es-AR    Spanish (Argentina)
 Español (Bolivia)    es-BO    Spanish (Bolivia)
 Español (Chile)    es-CL    Spanish (Chile)
 Español (Colombia)    es-CO    Spanish (Colombia)
 Español (Costa Rica)    es-CR    Spanish (Costa Rica)
 Español (Ecuador)    es-EC    Spanish (Ecuador)
 Español (El Salvador)    es-SV    Spanish (El Salvador)
 Español (España)    es-ES    Spanish (Spain)
 Español (Estados Unidos)    es-US    Spanish (United States)
 Español (Guatemala)    es-GT    Spanish (Guatemala)
 Español (Honduras)    es-HN    Spanish (Honduras)
 Español (México)    es-MX    Spanish (Mexico)
 Español (Nicaragua)    es-NI    Spanish (Nicaragua)
 Español (Panamá)    es-PA    Spanish (Panama)
 Español (Paraguay)    es-PY    Spanish (Paraguay)
 Español (Perú)    es-PE    Spanish (Peru)
 Español (Puerto Rico)    es-PR    Spanish (Puerto Rico)
 Español (República Dominicana)    es-DO    Spanish (Dominican Republic)
 Español (Uruguay)    es-UY    Spanish (Uruguay)
 Español (Venezuela)    es-VE    Spanish (Venezuela)
 Euskara (Espainia)    eu-ES    Basque (Spain)
 Filipino (Pilipinas)    fil-PH    Filipino (Philippines)
 Français (Canada)    fr-CA    French (Canada)
 Français (France)    fr-FR    French (France)
 Galego (España)    gl-ES    Galician (Spain)
 ქართული (საქართველო)    ka-GE    Georgian (Georgia)
 ગુજરાતી (ભારત)    gu-IN    Gujarati (India)
 Hrvatski (Hrvatska)    hr-HR    Croatian (Croatia)
 IsiZulu (Ningizimu Afrika)    zu-ZA    Zulu (South Africa)
 Íslenska (Ísland)    is-IS    Icelandic (Iceland)
 Italiano (Italia)    it-IT    Italian (Italy)
 Jawa (Indonesia)    jv-ID    Javanese (Indonesia)
 ಕನ್ನಡ (ಭಾರತ)    kn-IN    Kannada (India)
 ភាសាខ្មែរ (កម្ពុជា)    km-KH    Khmer (Cambodia)
 ລາວ (ລາວ)    lo-LA    Lao (Laos)
 Latviešu (latviešu)    lv-LV    Latvian (Latvia)
 Lietuvių (Lietuva)    lt-LT    Lithuanian (Lithuania)
 Magyar (Magyarország)    hu-HU    Hungarian (Hungary)
 മലയാളം (ഇന്ത്യ)    ml-IN    Malayalam (India)
 मराठी (भारत)    mr-IN    Marathi (India)
 Nederlands (Nederland)    nl-NL    Dutch (Netherlands)
 नेपाली (नेपाल)    ne-NP    Nepali (Nepal)
 Norsk bokmål (Norge)    nb-NO    Norwegian Bokmål (Norway)
 Polski (Polska)    pl-PL    Polish (Poland)
 Português (Brasil)    pt-BR    Portuguese (Brazil)
 Português (Portugal)    pt-PT    Portuguese (Portugal)
 Română (România)    ro-RO    Romanian (Romania)
 සිංහල (ශ්රී ලංකාව)    si-LK    Sinhala (Sri Lanka)
 Slovenčina (Slovensko)    sk-SK    Slovak (Slovakia)
 Slovenščina (Slovenija)    sl-SI    Slovenian (Slovenia)
 Urang (Indonesia)    su-ID    Sundanese (Indonesia)
 Swahili (Tanzania)    sw-TZ    Swahili (Tanzania)
 Swahili (Kenya)    sw-KE    Swahili (Kenya)
 Suomi (Suomi)    fi-FI    Finnish (Finland)
 Svenska (Sverige)    sv-SE    Swedish (Sweden)
 தமிழ் (இந்தியா)    ta-IN    r (India)
 தமிழ் (சிங்கப்பூர்)    ta-SG    Tamil (Singapore)
 தமிழ் (இலங்கை)    ta-LK    Tamil (Sri Lanka)
 தமிழ் (மலேசியா)    ta-MY    Tamil (Malaysia)
 తెలుగు (భారతదేశం)    te-IN    Telugu (India)
 Tiếng Việt (Việt Nam)    vi-VN    Vietnamese (Vietnam)
 Türkçe (Türkiye)    tr-TR    Turkish (Turkey)
 اردو (پاکستان)    ur-PK    Urdu (Pakistan)
 اردو (بھارت)    ur-IN    Urdu (India)
 Ελληνικά (Ελλάδα)    el-GR    Greek (Greece)
 Български (България)    bg-BG    Bulgarian (Bulgaria)
 Русский (Россия)    ru-RU    Russian (Russia)
 Српски (Србија)    sr-RS    Serbian (Serbia)
 Українська (Україна)    uk-UA    Ukrainian (Ukraine)
 עברית (ישראל)    he-IL    Hebrew (Israel)
 العربية (إسرائيل)    ar-IL    Arabic (Israel)
 العربية (الأردن)    ar-JO    Arabic (Jordan)
 العربية (الإمارات)    ar-AE    Arabic (United Arab Emirates)
 العربية (البحرين)    ar-BH    Arabic (Bahrain)
 العربية (الجزائر)    ar-DZ    Arabic (Algeria)
 العربية (السعودية)    ar-SA    Arabic (Saudi Arabia)
 العربية (العراق)    ar-IQ    Arabic (Iraq)
 العربية (الكويت)    ar-KW    Arabic (Kuwait)
 العربية (المغرب)    ar-MA    Arabic (Morocco)
 العربية (تونس)    ar-TN    Arabic (Tunisia)
 العربية (عُمان)    ar-OM    Arabic (Oman)
 العربية (فلسطين)    ar-PS    Arabic (State of Palestine)
 العربية (قطر)    ar-QA    Arabic (Qatar)
 العربية (لبنان)    ar-LB    Arabic (Lebanon)
 العربية (مصر)    ar-EG    Arabic (Egypt)
 فارسی (ایران)    fa-IR    Persian (Iran)
 हिन्दी (भारत)    hi-IN    Hindi (India)
 ไทย (ประเทศไทย)    th-TH    Thai (Thailand)
 한국어 (대한민국)    ko-KR    Korean (South Korea)
 國語 (台灣)    cmn-Hant-TW    Chinese, Mandarin (Traditional, Taiwan)
 廣東話 (香港)    yue-Hant-HK    Chinese, Cantonese (Traditional, Hong Kong)
 日本語（日本）    ja-JP    Japanese (Japan)
 普通話 (香港)    cmn-Hans-HK    Chinese, Mandarin (Simplified, Hong Kong)
 普通话 (中国大陆)    cmn-Hans-CN    Chinese, Mandarin (Simplified, China)
 */

@end
