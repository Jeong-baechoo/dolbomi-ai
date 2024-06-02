import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

class ApiService {
  static const String baseUrl = '';

  // static Future<UserModel> getUserInfo() {
  //   UserModel user;
  //   final url = Uri.parse('$baseUrl/user');
  //   final response = await http.get(url);
  //   if (response.statusCode == 200) {
  //     final user = jsonDecode(response.body);
  //   }
  //   return user;
  // }

  // getResponse(){}

  // postUserMessage(){}

  // gethistory(){}
}
