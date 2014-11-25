BEGIN;
UPDATE LotEntry JOIN MemberGroup ON LotEntry.membergroup_id=MemberGroup.id SET LotEntry.membership_id=MemberGroup.membership_id WHERE LotEntry.membership_id IS NULL;
UPDATE LotEntry JOIN UserCredential ON LotEntry.user_id=UserCredential.user_id SET LotEntry.membership_id=UserCredential.membership_id WHERE LotEntry.membership_id IS NULL;
UPDATE Cart JOIN Performance ON Cart.performance_id=Performance.id JOIN EventSetting ON EventSetting.event_id=Performance.event_id SET Cart.cart_setting_id=EventSetting.cart_setting_id WHERE Cart.cart_setting_id IS NULL;
UPDATE `Order` JOIN `UserCredential` ON `Order`.user_id=`UserCredential`.user_id SET `Order`.membership_id=`UserCredential`.membership_id WHERE `Order`.membership_id IS NULL;
UPDATE `Order` JOIN `Member` ON `Order`.user_id=`Member`.user_id JOIN `MemberGroup` ON `Member`.membergroup_id=`MemberGroup`.id SET `Order`.membership_id=`MemberGroup`.membership_id WHERE `Order`.membership_id IS NULL AND `Member`.deleted_at IS NULL AND `MemberGroup`.deleted_at IS NULL;
UPDATE `Order` JOIN `Organization` ON `Order`.organization_id=`Organization`.id JOIN `Membership` ON `Order`.organization_id=`Membership`.organization_id AND `Membership`.name=`Organization`.short_name SET `Order`.membership_id=`Membership`.id WHERE `Order`.membership_id IS NULL;
COMMIT;
