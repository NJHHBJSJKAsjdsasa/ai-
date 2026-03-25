import re
import json
import base64


class PrivacyDetector:
    """隐私检测工具类"""

    def __init__(self):
        self.encryption_key = 0x5A

    def detect_bank_card(self, content: str) -> list:
        """检测银行卡号（16-19位数字，可能带空格）"""
        if not content:
            return []

        pattern = r'\b(?:\d{4}[\s-]?){3,4}\d{1,4}\b|\b\d{16,19}\b'
        matches = re.findall(pattern, content)

        valid_cards = []
        for match in matches:
            digits = re.sub(r'[\s-]', '', match)
            if 16 <= len(digits) <= 19:
                valid_cards.append(match)

        return valid_cards

    def detect_phone(self, content: str) -> list:
        """检测手机号（11位，1开头）"""
        if not content:
            return []

        pattern = r'\b1[3-9]\d{9}\b'
        return re.findall(pattern, content)

    def detect_id_card(self, content: str) -> list:
        """检测身份证号（18位，含X）"""
        if not content:
            return []

        pattern = r'\b\d{17}[\dXx]\b'
        matches = re.findall(pattern, content)

        valid_ids = []
        for match in matches:
            if self._validate_id_card(match):
                valid_ids.append(match)

        return valid_ids

    def _validate_id_card(self, id_card: str) -> bool:
        """简单验证身份证号格式"""
        if len(id_card) != 18:
            return False

        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

        try:
            sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
            check_code = check_codes[sum_value % 11]
            return id_card[-1].upper() == check_code
        except ValueError:
            return False

    def detect_password(self, content: str) -> list:
        """检测密码/密钥（包含"密码"、"password"等关键词）"""
        if not content:
            return []

        patterns = [
            r'(?:密码|password|pwd|passwd|密钥|secret|key)[\s:=]+["\']?([^"\'\s]{4,})["\']?',
            r'(?:api[_-]?key|apikey|token)[\s:=]+["\']?([^"\'\s]{8,})["\']?',
        ]

        passwords = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            passwords.extend(matches)

        return passwords

    def assess_privacy_risk(self, content: str) -> int:
        """评估隐私风险等级 (0-100)"""
        if not content:
            return 0

        risk_score = 0

        if self.detect_bank_card(content):
            risk_score = max(risk_score, 100)

        if self.detect_phone(content):
            risk_score = max(risk_score, 80)

        if self.detect_id_card(content):
            risk_score = max(risk_score, 90)

        if self.detect_password(content):
            risk_score = max(risk_score, 100)

        return risk_score

    def should_store(self, content: str) -> bool:
        """判断是否允许存储"""
        risk_score = self.assess_privacy_risk(content)
        return risk_score < 80

    def mask_sensitive_info(self, content: str) -> str:
        """脱敏处理敏感信息"""
        if not content:
            return content

        masked = content

        for card in self.detect_bank_card(content):
            digits = re.sub(r'[\s-]', '', card)
            masked_card = digits[:4] + '*' * (len(digits) - 8) + digits[-4:]
            masked = masked.replace(card, masked_card)

        for phone in self.detect_phone(content):
            masked_phone = phone[:3] + '****' + phone[-4:]
            masked = masked.replace(phone, masked_phone)

        for id_card in self.detect_id_card(content):
            masked_id = id_card[:6] + '********' + id_card[-4:]
            masked = masked.replace(id_card, masked_id)

        passwords = self.detect_password(content)
        for pwd in passwords:
            masked_pwd = '*' * len(pwd)
            masked = re.sub(rf'(["\']?){re.escape(pwd)}(["\']?)', rf'\1{masked_pwd}\2', masked)

        return masked

    def encrypt_sensitive_info(self, content: str) -> str:
        """加密敏感信息（使用简单异或加密）"""
        if not content:
            return content

        encrypted = bytearray()
        for byte in content.encode('utf-8'):
            encrypted.append(byte ^ self.encryption_key)

        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_sensitive_info(self, encrypted: str) -> str:
        """解密敏感信息"""
        if not encrypted:
            return encrypted

        try:
            encrypted_bytes = base64.b64decode(encrypted)
            decrypted = bytearray()
            for byte in encrypted_bytes:
                decrypted.append(byte ^ self.encryption_key)
            return decrypted.decode('utf-8')
        except Exception:
            return encrypted

    def analyze(self, content: str) -> dict:
        """综合分析，返回检测结果字典"""
        if not content:
            return {
                'content_length': 0,
                'has_sensitive_info': False,
                'risk_score': 0,
                'risk_level': 'none',
                'detections': {},
                'can_store': True,
                'recommendation': '内容为空，无风险'
            }

        bank_cards = self.detect_bank_card(content)
        phones = self.detect_phone(content)
        id_cards = self.detect_id_card(content)
        passwords = self.detect_password(content)

        risk_score = self.assess_privacy_risk(content)

        if risk_score >= 100:
            risk_level = 'critical'
            recommendation = '检测到高风险敏感信息，建议立即处理'
        elif risk_score >= 90:
            risk_level = 'high'
            recommendation = '检测到高敏感信息，建议谨慎处理'
        elif risk_score >= 80:
            risk_level = 'medium'
            recommendation = '检测到敏感信息，建议评估后处理'
        elif risk_score > 0:
            risk_level = 'low'
            recommendation = '检测到潜在敏感信息，建议关注'
        else:
            risk_level = 'none'
            recommendation = '未检测到敏感信息，可正常处理'

        return {
            'content_length': len(content),
            'has_sensitive_info': risk_score > 0,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'detections': {
                'bank_cards': {
                    'count': len(bank_cards),
                    'items': bank_cards
                },
                'phones': {
                    'count': len(phones),
                    'items': phones
                },
                'id_cards': {
                    'count': len(id_cards),
                    'items': id_cards
                },
                'passwords': {
                    'count': len(passwords),
                    'items': ['***' * len(pwd) for pwd in passwords]
                }
            },
            'can_store': self.should_store(content),
            'recommendation': recommendation
        }
