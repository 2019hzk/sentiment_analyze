from atguigu.engines.agent.host.section.listener import section_ready_listener


class AppLifecycleManager:
    """应用生命周期管理器:统一启动与关闭后台服务组件及引擎共享资源"""

    def register(self):
        """统一注册并启动所有关联的后台服务组件"""

        # 1. 启动实时广播服务 (TODO )
        # 2. 启动 Host 章节研判监听器
        section_ready_listener.start()

    async def shutdown(self):
        """统一注销并停止所有关联的后台服务组件,释放持有的资源"""

        # 1. 停止实时广播服务，断开事件订阅(TODO )
        # 2. 停止 Host 章节监听 worker
        section_ready_listener.stop()


lifecycle_manager = AppLifecycleManager()
