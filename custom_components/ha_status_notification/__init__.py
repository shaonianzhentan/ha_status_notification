import os, uuid, logging, requests

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_status_notification'

def setup(hass, config):
    cfg = config[DOMAIN]
    key = cfg.get('key')

    def handle_event(event):
        data = event.data
        # 更改时间
        changed_time = data.get('time_fired')
        old_state = data.get('old_state')
        new_state = data.get('new_state')
        # 状态一致时，发送通知消息
        if old_state['state'] != new_state['state']:
            attr = new_state['attributes']
            friendly_name = attr['friendly_name']
            msg = f"{friendly_name}当前状态：{new_state['state']}"
            r = requests.get(f"https://go.bemfa.com/v1/sendwechat?uid={key}&msg={msg}")
            print(r.json())

    hass.bus.listen("state_changed", handle_event)
    return True