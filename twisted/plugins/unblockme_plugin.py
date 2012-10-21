from twisted.application.service import ServiceMaker

finger = ServiceMaker(
    'unblockme',
    'unblockme.tap',
    'service for bypassing geo-blocked websites',
    'unblockme'
)
