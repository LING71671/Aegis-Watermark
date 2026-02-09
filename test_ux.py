import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
from aegis.core.signature import SignatureManager
from aegis.cli import run_settings_wizard, MESSAGES

class TestUXRefactor(unittest.TestCase):
    def setUp(self):
        # 使用临时目录进行测试
        self.test_dir = "test_identities"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.sig_mgr = SignatureManager(keys_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('questionary.select')
    @patch('questionary.text')
    @patch('questionary.confirm')
    def test_multi_identity_creation(self, mock_confirm, mock_text, mock_select):
        # 模拟创建第一个身份 (default)
        mock_select.return_value.ask.side_effect = ["新建身份证书 (RSA)", "BACK (返回上一级)"]
        mock_confirm.return_value.ask.return_value = True
        mock_text.return_value.ask.side_effect = ["User1", "user1@example.com"]
        
        with patch('aegis.cli.sig_mgr', self.sig_mgr):
            run_settings_wizard()
        
        identities = self.sig_mgr.list_identities()
        self.assertIn("default", identities)
        
        # 模拟创建第二个身份 (work)
        mock_select.return_value.ask.side_effect = ["新建身份证书 (RSA)", "BACK (返回上一级)"]
        mock_confirm.return_value.ask.side_effect = [True, True]
        mock_text.return_value.ask.side_effect = ["work", "User Work", "work@example.com"]
        
        with patch('aegis.cli.sig_mgr', self.sig_mgr):
            run_settings_wizard()
            
        identities = self.sig_mgr.list_identities()
        self.assertIn("default", identities)
        self.assertIn("work", identities)
        self.assertEqual(len(identities), 2)

    @patch('questionary.text')
    @patch('questionary.path')
    @patch('questionary.confirm')
    @patch('questionary.select')
    def test_embed_wizard_and_back(self, mock_select, mock_confirm, mock_path, mock_text):
        from aegis.cli import run_embed_wizard
        
        # 1. 测试 :b 回退
        mock_path.return_value.ask.return_value = ":b"
        run_embed_wizard()
        self.assertEqual(mock_text.call_count, 0)
        
        # 2. 测试完整的确认页流程
        test_file = "test_file.png"
        with open(test_file, "w") as f: f.write("dummy")
        
        mock_path.return_value.ask.return_value = test_file
        mock_text.return_value.ask.side_effect = ["", "TEST", ""]
        mock_confirm.return_value.ask.side_effect = [True, True]
        
        with patch('aegis.cli.run_embed') as mock_run_embed:
            with patch('aegis.cli.sig_mgr', self.sig_mgr):
                self.sig_mgr.create_identity("Test", "test@test.com")
                run_embed_wizard()
                self.assertTrue(mock_run_embed.called)
        
        if os.path.exists(test_file): os.remove(test_file)

if __name__ == '__main__':
    unittest.main()