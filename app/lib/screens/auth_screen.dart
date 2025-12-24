import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.onLogin});
  final void Function(String token) onLogin;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';
  bool _isLogin = true;
  bool _loading = false;
  String? _error;
  final ApiService _api = ApiService('http://localhost:8000', null);

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    _formKey.currentState!.save();
    try {
      if (_isLogin) {
        final token = await _api.login(_email, _password);
        widget.onLogin(token);
      } else {
        await _api.register(_email, _password);
        final token = await _api.login(_email, _password);
        widget.onLogin(token);
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome')),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Text(_isLogin ? 'Sign in' : 'Create account', style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 12),
              if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      decoration: const InputDecoration(labelText: 'Email'),
                      onSaved: (v) => _email = v ?? '',
                      validator: (v) => v != null && v.contains('@') ? null : 'Enter a valid email',
                    ),
                    TextFormField(
                      decoration: const InputDecoration(labelText: 'Password'),
                      obscureText: true,
                      onSaved: (v) => _password = v ?? '',
                      validator: (v) => (v?.length ?? 0) >= 6 ? null : 'Min 6 chars',
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading ? const CircularProgressIndicator() : Text(_isLogin ? 'Login' : 'Register'),
                    ),
                    TextButton(
                      onPressed: () => setState(() => _isLogin = !_isLogin),
                      child: Text(_isLogin ? 'Create account' : 'Have an account? Login'),
                    )
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
