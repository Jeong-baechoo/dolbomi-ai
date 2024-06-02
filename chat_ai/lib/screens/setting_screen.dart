import '../widgets/setting_section_title.dart';
import '../widgets/setting_user_title.dart';
import 'package:flutter/material.dart';

class UserSettingsScreen extends StatelessWidget {
  const UserSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        foregroundColor: Colors.white,
        backgroundColor: Colors.black,
        title: const Text('사용자 설정'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SettingUserTitle(userName: "홍길동"),
              settingSectionTitle(
                "나이",
                "72",
              ),
              settingSectionTitle(
                "직업",
                "정년 은퇴 선생님",
              ),
              settingSectionTitle(
                '주거지',
                '대한민국 서울',
              ),
              settingSectionTitle(
                "학력",
                "교육대학 수학교육학과 졸업",
              ),
              settingSectionTitle(
                '앓고 있는 질병',
                '당뇨\n고혈압\n무릎 관절염',
              ),
              settingSectionTitle(
                '가족관계',
                '아내\n첫째 아들 며느리 손자 1명\n둘째 딸 사위 손자1명 손녀1명',
              ),

              const SizedBox(
                height: 20,
              ),
              // Edit Button
              Center(
                child: ElevatedButton(
                  onPressed: () {
                    // Add functionality for edit
                  },
                  style: ElevatedButton.styleFrom(
                    foregroundColor: Colors.black,
                    backgroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 40, vertical: 15),
                  ),
                  child: const Text(
                    '수정하기',
                    style: TextStyle(fontSize: 20),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
