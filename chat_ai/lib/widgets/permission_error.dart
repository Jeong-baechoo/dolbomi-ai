import 'package:flutter/material.dart';

class PermissionNotAbleWindow extends StatelessWidget {
  const PermissionNotAbleWindow({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('권한 오류'),
      content: const Text('마이크 권한이 부여되지 않았습니다'),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('확인'),
        ),
      ],
    );
  }
}
