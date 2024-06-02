class UserModel {
  final String name,
      age,
      profession,
      location,
      education,
      healthWellness,
      importantRelationship;

  UserModel.fromJson(Map<String, dynamic> json)
      : name = json['name'],
        age = json['age'],
        profession = json['profession'],
        location = json['location'],
        education = json['education'],
        healthWellness = json['health_wellness'],
        importantRelationship = json['important_relationship'];
}
