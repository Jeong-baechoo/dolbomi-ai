import 'package:flutter/material.dart';

class SettingUserTitle extends StatelessWidget {
  final String userName;

  const SettingUserTitle({
    super.key,
    required this.userName,
  });

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        CircleAvatar(
          radius: 40,
          backgroundColor: Colors.white,
          child: Icon(
            Icons.person,
            size: 50,
            color: Colors.black,
          ),
        ),
        SizedBox(width: 20),
        Text(
          '홍길동',
          style: TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
