import os, uuid, logging, requests

_LOGGER = logging.getLogger(__name__)

from homeassistant.const import CONF_TOKEN, STATE_OFF, STATE_ON, STATE_NOT_HOME, STATE_HOME, \
    STATE_UNAVAILABLE,  STATE_PLAYING, STATE_PAUSED, STATE_IDLE

from .translations import weather_state, sun_state

DOMAIN = 'ha_status_notification'
VERSION = '1.1'

def setup(hass, config):
    cfg = config[DOMAIN]
    token = cfg.get(CONF_TOKEN)

    def send_msg(msg):
        r = requests.get(f"https://go.bemfa.com/v1/sendwechat?uid={token}&msg={msg}&time=1")
        print(r.json())

    def handle_event(event):
        data = event.data
        # 更改时间
        changed_time = data.get('time_fired')
        old_state = data.get('old_state')
        new_state = data.get('new_state')
        # 状态一致时，发送通知消息
        if old_state is not None and new_state is not None \
            and ['binary_sensor.updater'].count(new_state.entity_id) == 0 \
            and old_state.state != new_state.state:
            attr = new_state.attributes
            friendly_name = attr['friendly_name']
            msg = ''
            if new_state.state == STATE_ON:
                msg = f"【{friendly_name}】开启"
            elif new_state.state == STATE_NOT_HOME:
                msg = f"【{friendly_name}】不在家"
            elif new_state.state == STATE_HOME:
                msg = f"【{friendly_name}】在家"

            # 不可用提示
            if new_state.state == STATE_UNAVAILABLE:
                return send_msg(f"【{friendly_name}】不可用")

            # 人体传感器
            if new_state.domain == 'binary_sensor':
                device_class = attr.get('device_class', '')
                if new_state.state == STATE_ON:
                    if device_class == 'motion':
                        msg = f"【{friendly_name}】检测到有人"

            # 脚本
            elif new_state.domain == 'script':
                if new_state.state == STATE_ON:
                    msg = f"【{friendly_name}】已执行"

            # 媒体播放器
            elif new_state.domain == 'media_player':
                if new_state.state == STATE_PLAYING:
                    msg = f"【{friendly_name}】正在播放：{attr.get('media_title', '')}"
                elif new_state.state == STATE_PAUSED:
                    msg = f"【{friendly_name}】暂停播放"

            # 开关
            elif ['switch', 'input_boolean', 'light'].count(new_state.domain) > 0:
                if new_state.state == STATE_ON:
                    msg = f"【{friendly_name}】已打开"
                elif new_state.state == STATE_OFF:
                    msg = f"【{friendly_name}】已关闭"

            # 天气
            elif new_state.domain == 'weather':
                msg = f"【{friendly_name}】天气：{weather_state[new_state.state]}，当前温度：{attr.get('temperature')}，湿度：{attr.get('humidity')}，风速：{attr.get('wind_speed')}"

            # 太阳
            elif new_state.domain == 'sun':
                msg = f"【{friendly_name}】{sun_state[new_state.state]}"

            # 发送通知
            if msg != '':
                send_msg(msg)

    hass.bus.listen("state_changed", handle_event)

    # 通知
    def notify_message(call):
        data = call.data
        if 'message' in data:
            send_msg(data.get('message'))

    hass.services.register(DOMAIN, 'notify', notify_message)
    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    状态提醒【作者QQ：635147515】
    
    版本：''' + VERSION + '''
        
    项目地址：https://github.com/shaonianzhentan/ha_status_notification
-------------------------------------------------------------------''')
    return True