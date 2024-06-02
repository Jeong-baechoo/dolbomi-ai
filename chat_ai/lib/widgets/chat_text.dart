import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

class ChatText extends StatefulWidget {
  final String message;
  final bool isUser;

  const ChatText({
    super.key,
    required this.isUser,
    required this.message,
  });

  @override
  State<ChatText> createState() => ChatTextState();
}

class ChatTextState extends State<ChatText> {
  final FlutterTts _flutterTts = FlutterTts();
  Map? _currentVoice;
  List<Map> voices = [];

  @override
  void initState() {
    super.initState();
    initTTS();
  }

  void initTTS() async {
    await _flutterTts.getVoices.then((data) {
      try {
        voices = List<Map>.from(data);
        setState(() {
          voices =
              voices.where((voice) => voice["name"].contains("ko")).toList();
          _currentVoice = voices.first;
          setVoice(_currentVoice!);
        });
      } catch (e) {
        print(e);
      }
    });
    _flutterTts.setLanguage("ko-KR");
  }

  void setVoice(Map voice) {
    _flutterTts.setVoice({"name": voice["name"], "locale": voice["locale"]});
  }

  void speakVoice() {
    if (widget.isUser == false) {
      _flutterTts.speak(widget.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    // if (widget.isUser == false) {
    //   _flutterTts.speak(widget.message);
    // }

    return Padding(
      padding: widget.isUser
          ? const EdgeInsets.fromLTRB(40.0, 0, 60.0, 0)
          : const EdgeInsets.fromLTRB(60.0, 0, 40.0, 0),
      child: Align(
        alignment: widget.isUser ? Alignment.centerLeft : Alignment.centerRight,
        child: Column(
          crossAxisAlignment:
              widget.isUser ? CrossAxisAlignment.start : CrossAxisAlignment.end,
          children: [
            Text(
              widget.isUser ? 'User' : 'System',
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 25,
                  fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              widget.message,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 26,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
