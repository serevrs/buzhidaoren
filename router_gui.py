from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
                           QMessageBox, QGroupBox, QStatusBar, QHeaderView, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from routeros_api import RouterOsApiPool

class RouterManager:
    def __init__(self, host, username, password, port=6728):
        self.api = RouterOsApiPool(
            host=host,
            username=username,
            password=password,
            port=port,
            plaintext_login=True
        ).get_api()
        
    def get_system_status(self):
        """获取系统状态"""
        try:
            system = self.api.get_resource('/system/resource')
            return system.get()[0]
        except Exception as e:
            raise Exception(f"获取系统状态失败: {str(e)}")
    
    def close(self):
        """关闭连接"""
        if self.api:
            self.api.close()

class MikrotikGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置应用图标
        self.setWindowIcon(QIcon('icon.svg'))
        
        # 初始化路由器连接
        self.router = None
        self.run_count = 0
        
        # 加载运行次数
        self.run_count = self.load_run_count()
        self.run_count += 1
        self.save_run_count()
        
        # 系统状态项目的中文映射
        self.status_translations = {
            'uptime': '运行时间',
            'version': '系统版本',
            'cpu-load': 'CPU负载',
            'cpu-count': 'CPU数量',
            'cpu-frequency': 'CPU频率',
            'free-memory': '可用内存',
            'total-memory': '总内存',
            'free-hdd-space': '可用硬盘空间',
            'total-hdd-space': '总硬盘空间',
            'architecture-name': '系统架构',
            'board-name': '设备型号',
            'platform': '平台'
        }
        
        self.initUI()

    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('牛犇网络Routeros软路由管理工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 登录组
        login_group = QGroupBox("路由器连接")
        login_layout = QGridLayout()
        login_group.setLayout(login_layout)
        
        # 添加输入框和标签
        input_layout = QHBoxLayout()
        
        # 主机地址输入
        host_layout = QVBoxLayout()
        host_label = QLabel("主机:")
        self.host_input = QLineEdit()
        self.host_input.setText('192.168.88.254')  # 默认主机地址
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        input_layout.addLayout(host_layout)
        
        # 端口输入
        port_layout = QVBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QLineEdit('6728')  # 默认端口
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        input_layout.addLayout(port_layout)
        
        # 用户名输入
        username_layout = QVBoxLayout()
        username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        self.username_input.setText('houtai')  # 默认用户名
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        input_layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QVBoxLayout()
        password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setText('houtai')  # 默认密码
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        input_layout.addLayout(password_layout)
        
        login_layout.addLayout(input_layout, 0, 0, 1, 4)
        
        # 添加连接按钮
        self.connect_btn = QPushButton("登录")
        self.connect_btn.clicked.connect(self.on_connect)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        login_layout.addWidget(self.connect_btn, 1, 0, 1, 4)
        
        # 添加一键随机路由硬件信息按钮
        random_btn = QPushButton("一键随机路由硬件信息")
        random_btn.clicked.connect(self.randomize_hardware_info)
        random_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;  /* 蓝色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        login_layout.addWidget(random_btn, 2, 0, 1, 4)
        
        # 添加模式切换按钮布局
        mode_layout = QHBoxLayout()
        
        # 本地模式按钮
        self.local_mode_btn = QPushButton("本地模式")
        self.local_mode_btn.clicked.connect(self.switch_to_local)
        self.local_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;  /* 橙色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """)
        mode_layout.addWidget(self.local_mode_btn)
        
        # VPN模式按钮
        self.vpn_mode_btn = QPushButton("VPN模式")
        self.vpn_mode_btn.clicked.connect(self.switch_to_vpn)
        self.vpn_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;  /* 紫色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        mode_layout.addWidget(self.vpn_mode_btn)
        
        login_layout.addLayout(mode_layout, 3, 0, 1, 4)
        
        main_layout.addWidget(login_group)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 系统状态标签页
        status_tab = QWidget()
        status_layout = QVBoxLayout()
        
        # 系统状态表格
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(2)
        self.status_table.setHorizontalHeaderLabels(['项目', '值'])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        status_layout.addWidget(self.status_table)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新状态")
        refresh_btn.clicked.connect(self.update_status)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;  /* 蓝灰色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        status_layout.addWidget(refresh_btn)
        
        status_tab.setLayout(status_layout)
        self.tabs.addTab(status_tab, "系统状态")
        
        # VPN设置标签页
        vpn_tab = QWidget()
        vpn_layout = QVBoxLayout()
        self.vpn_table = QTableWidget()
        self.vpn_table.setColumnCount(6)
        self.vpn_table.setHorizontalHeaderLabels(['类型', '名称', '目标地址', '用户名', '状态', '已连接'])
        
        # 设置列宽
        self.vpn_table.setColumnWidth(0, 100)  # 类型列
        self.vpn_table.setColumnWidth(1, 150)  # 名称列
        self.vpn_table.setColumnWidth(2, 150)  # 目标地址列
        self.vpn_table.setColumnWidth(3, 100)  # 用户名列
        self.vpn_table.setColumnWidth(4, 100)  # 状态列
        self.vpn_table.setColumnWidth(5, 100)  # 已连接列
        
        vpn_btn_layout = QHBoxLayout()
        self.refresh_vpn_btn = QPushButton("刷新VPN")
        self.refresh_vpn_btn.clicked.connect(self.update_vpn)
        self.refresh_vpn_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;  /* 蓝灰色 */
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        vpn_btn_layout.addWidget(self.refresh_vpn_btn)
        
        vpn_layout.addWidget(self.vpn_table)
        vpn_layout.addLayout(vpn_btn_layout)
        vpn_tab.setLayout(vpn_layout)
        self.tabs.addTab(vpn_tab, "VPN设置")
        
        main_layout.addWidget(self.tabs)
        
        self.tabs.setEnabled(False)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status_bar()  # 更新状态栏显示

    def update_status_bar(self):
        """更新状态栏显示"""
        self.statusBar.showMessage(f'程序已运行 {self.run_count} 次')

    def load_run_count(self):
        try:
            with open('run_count.txt', 'r') as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def save_run_count(self):
        with open('run_count.txt', 'w') as f:
            f.write(str(self.run_count))
            
    def update_status(self):
        """更新系统状态信息"""
        try:
            system = self.router.api.get_resource('/system/resource').get()[0]
            
            # 设置表格行数
            self.status_table.setRowCount(len(system))
            
            # 填充数据
            for i, (key, value) in enumerate(system.items()):
                # 项目名称（使用中文映射）
                item_name = QTableWidgetItem(self.status_translations.get(key, key))
                self.status_table.setItem(i, 0, item_name)
                
                # 项目值
                if key == 'cpu-load':
                    formatted_value = f"{value}%"
                elif key in ['free-memory', 'total-memory']:
                    try:
                        # 转换为MB
                        mb_value = int(value) / (1024 * 1024)
                        formatted_value = f"{mb_value:.2f} MB"
                    except:
                        formatted_value = str(value)
                elif key in ['free-hdd-space', 'total-hdd-space']:
                    try:
                        # 转换为MB
                        mb_value = int(value) / (1024 * 1024)
                        formatted_value = f"{mb_value:.2f} MB"
                    except:
                        formatted_value = str(value)
                elif key == 'cpu-frequency':
                    formatted_value = f"{value} MHz"
                elif key == 'uptime':
                    # RouterOS的运行时间格式是类似"63d02:31:30"这样的格式
                    # 尝试将其转换为更友好的格式
                    try:
                        # 提取天数和时间部分
                        if 'd' in str(value):
                            days, time_part = str(value).split('d')
                            hours, minutes, seconds = time_part.split(':')
                            formatted_value = f"{days}天 {hours}小时 {minutes}分钟 {seconds}秒"
                        else:
                            hours, minutes, seconds = str(value).split(':')
                            formatted_value = f"{hours}小时 {minutes}分钟 {seconds}秒"
                    except:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                item_value = QTableWidgetItem(formatted_value)
                item_value.setTextAlignment(Qt.AlignCenter)  # 居中对齐
                self.status_table.setItem(i, 1, item_value)
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新系统状态失败: {str(e)}")
            
    def update_vpn(self):
        """更新VPN拨号列表"""
        try:
            # 获取所有类型的VPN客户端
            vpn_clients = []
            
            # PPTP客户端
            pptp_clients = self.router.api.get_resource('/interface/pptp-client').get()
            for client in pptp_clients:
                client['type'] = 'PPTP'
                vpn_clients.append(client)
            
            # L2TP客户端
            l2tp_clients = self.router.api.get_resource('/interface/l2tp-client').get()
            for client in l2tp_clients:
                client['type'] = 'L2TP'
                vpn_clients.append(client)
            
            # SSTP客户端
            sstp_clients = self.router.api.get_resource('/interface/sstp-client').get()
            for client in sstp_clients:
                client['type'] = 'SSTP'
                vpn_clients.append(client)
            
            # OVPN客户端
            ovpn_clients = self.router.api.get_resource('/interface/ovpn-client').get()
            for client in ovpn_clients:
                client['type'] = 'OpenVPN'
                vpn_clients.append(client)
            
            # 更新表格
            self.vpn_table.setRowCount(len(vpn_clients))
            
            for i, vpn in enumerate(vpn_clients):
                # 设置类型
                type_item = QTableWidgetItem(vpn.get('type', ''))
                type_item.setTextAlignment(Qt.AlignCenter)
                self.vpn_table.setItem(i, 0, type_item)
                
                # 设置名称
                name = QTableWidgetItem(vpn.get('name', ''))
                self.vpn_table.setItem(i, 1, name)
                
                # 设置目标地址
                connect_to = QTableWidgetItem(vpn.get('connect-to', ''))
                connect_to.setTextAlignment(Qt.AlignCenter)
                self.vpn_table.setItem(i, 2, connect_to)
                
                # 设置用户名
                user = QTableWidgetItem(vpn.get('user', ''))
                user.setTextAlignment(Qt.AlignCenter)
                self.vpn_table.setItem(i, 3, user)
                
                # 设置状态
                status = QTableWidgetItem(vpn.get('status', ''))
                status.setTextAlignment(Qt.AlignCenter)
                self.vpn_table.setItem(i, 4, status)
                
                # 设置已连接状态
                connected = QTableWidgetItem('是' if vpn.get('connected', '') == 'true' else '否')
                connected.setTextAlignment(Qt.AlignCenter)
                self.vpn_table.setItem(i, 5, connected)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取VPN列表失败: {str(e)}")
            
    def on_connect(self):
        try:
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            port = int(self.port_input.text())
            
            if not all([host, username, password]):
                QMessageBox.warning(self, "警告", "请填写所有连接信息！")
                return
                
            self.router = RouterManager(host, username, password, port)
            self.tabs.setEnabled(True)
            self.statusBar.showMessage('连接成功！程序已运行 {} 次'.format(self.run_count))
            QMessageBox.information(self, "成功", "已成功连接到路由器！")
            
            self.update_status()
            self.update_vpn()
            
        except ValueError:
            QMessageBox.critical(self, "错误", "端口必须是有效的数字！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接失败: {str(e)}")
            
    def switch_to_local(self):
        """切换到本地模式"""
        if not self.router:
            QMessageBox.warning(self, "警告", "请先登录路由器！")
            return
            
        try:
            self.router.api.get_resource('/system/script').call('run', {'number': 'qiebendi'})
            QMessageBox.information(self, "成功", "已切换到本地模式")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换模式失败: {str(e)}")
        
    def switch_to_vpn(self):
        """切换到VPN模式"""
        if not self.router:
            QMessageBox.warning(self, "警告", "请先登录路由器！")
            return
            
        try:
            self.router.api.get_resource('/system/script').call('run', {'number': 'qievpn'})
            QMessageBox.information(self, "成功", "已切换到VPN模式")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换模式失败: {str(e)}")
            
    def randomize_hardware_info(self):
        """一键随机路由硬件信息"""
        if not self.router:
            QMessageBox.warning(self, "警告", "请先连接到路由器！")
            return
            
        try:
            # 调用system script运行随机化脚本
            self.router.api.get_resource('/system/script').call('run', {'number': 'qiemac'})
            QMessageBox.information(self, "成功", "已成功随机化路由硬件信息！")
            
            # 更新系统状态显示
            self.update_status()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"随机化硬件信息失败: {str(e)}")
            
    def closeEvent(self, event):
        """关闭窗口时断开连接"""
        if self.router:
            self.router.close()
        event.accept()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gui = MikrotikGUI()
    gui.show()
    sys.exit(app.exec_())
