import 'package:flutter/material.dart';

Widget settingSectionTitle(String title, String content) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      const SizedBox(height: 10),
      const Divider(color: Colors.white, thickness: 1),
      Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      Text(
        content,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 18,
        ),
      ),
    ],
  );
}
