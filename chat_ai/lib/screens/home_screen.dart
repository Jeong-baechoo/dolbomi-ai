import '../screens/setting_screen.dart';
import '../widgets/permission_error.dart';
import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';
import '../widgets/chat_text.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final SpeechToText _speechToText = SpeechToText();
  bool _speechEnabled = false;
  String _wordsSpoken = "";
  String ansMessage = "";
  final GlobalKey<ChatTextState> systemChatKey = GlobalKey<ChatTextState>();

  @override
  void initState() {
    super.initState();
    initSpeech();
  }

  void initSpeech() async {
    _speechEnabled = await _speechToText.initialize();
    setState(() {});
  }

  void _startListening() async {
    await _speechToText.listen(
      onResult: _onSpeechReault,
      localeId: 'ko_KR',
    );
    setState(() {});
  }

  void _onSpeechReault(SpeechRecognitionResult result) {
    setState(() {
      _wordsSpoken = result.recognizedWords;
    });
  }

  void _stopListening() async {
    await _speechToText.stop();
    setState(() {});
  }

  void getAns() {
    ansMessage = "안녕하세요";
    systemChatKey.currentState?.speakVoice();
  }

  // getans 호출 로직 찾기

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        foregroundColor: Colors.white,
        backgroundColor: Colors.black,
        centerTitle: true,
        title: const Text(
          "돌봄이",
          style: TextStyle(fontWeight: FontWeight.w500, fontSize: 26),
        ),
        leading: IconButton(
          icon: const Icon(
            Icons.chat_rounded,
            size: 27,
          ),
          onPressed: () {},
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.settings,
              size: 35,
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const UserSettingsScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ChatText(
              isUser: true,
              message: _wordsSpoken,
            ),
            const SizedBox(height: 40),
            ChatText(
              key: systemChatKey,
              isUser: false,
              message: ansMessage,
            ),
            const SizedBox(height: 100),
            IconButton(
              icon: const Icon(
                Icons.mic,
                color: Colors.white,
                size: 50,
              ),
              onPressed: () {
                if (_speechEnabled == false) {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return const PermissionNotAbleWindow();
                    },
                  );
                } else {
                  _speechToText.isListening
                      ? _stopListening()
                      : _startListening();
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
