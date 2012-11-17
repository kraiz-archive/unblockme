from twisted.application.service import ServiceMaker

unblockme = ServiceMaker(
    'unblockme',
    'unblockme.tap',
    'service for bypassing geo-blocked websites',
    'unblockme'
)
