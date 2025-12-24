class Profile {
  final int id;
  final String name;
  final String? sex;
  final String? dob;
  final List<String> conditions;
  final List<String> meds;

  Profile({
    required this.id,
    required this.name,
    this.sex,
    this.dob,
    this.conditions = const [],
    this.meds = const [],
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'],
      name: json['name'],
      sex: json['sex'],
      dob: json['dob'],
      conditions: (json['conditions'] as List<dynamic>? ?? []).cast<String>(),
      meds: (json['meds'] as List<dynamic>? ?? []).cast<String>(),
    );
  }
}

class BiomarkerInsight {
  final String testName;
  final double value;
  final String unit;
  final String status;
  final double? refLow;
  final double? refHigh;
  final List<String> lifestyleTips;
  final List<String> redFlags;
  final Map<String, dynamic> compare;

  BiomarkerInsight({
    required this.testName,
    required this.value,
    required this.unit,
    required this.status,
    this.refLow,
    this.refHigh,
    this.lifestyleTips = const [],
    this.redFlags = const [],
    this.compare = const {},
  });

  factory BiomarkerInsight.fromJson(Map<String, dynamic> json) {
    return BiomarkerInsight(
      testName: json['test_name'],
      value: (json['value'] as num).toDouble(),
      unit: json['unit'],
      status: json['status'],
      refLow: (json['ref_low'] as num?)?.toDouble(),
      refHigh: (json['ref_high'] as num?)?.toDouble(),
      lifestyleTips: (json['lifestyle_tips'] as List<dynamic>? ?? []).cast<String>(),
      redFlags: (json['red_flags'] as List<dynamic>? ?? []).cast<String>(),
      compare: json['compare_to_previous'] ?? {},
    );
  }
}
