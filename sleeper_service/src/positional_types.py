@dataclass
class RunningBackStats:
    anytime_tds: int  # Total touchdowns scored at any time in the game
    bonus_fd_rb: int  # Bonus points awarded for first downs by running backs
    bonus_rec_rb: int  # Bonus points awarded for receptions by running backs
    bonus_rush_att_20: int  # Bonus points for rushing attempts over 20 yards
    bonus_rush_rec_yd_100: int  # Bonus for achieving 100 rushing or receiving yards
    fum: int  # Total fumbles by the player
    fum_lost: int  # Total fumbles lost by the player
    gp: int  # Games played
    gs: int  # Games started
    gms_active: int  # Games in which the player was active
    off_snp: int  # Number of snaps played on offense
    pass_rush_yd: int  # Yards gained from rushing attempts
    pos_rank_half_ppr: int  # Position rank in half-point per reception leagues
    pos_rank_ppr: int  # Position rank in point per reception leagues
    pos_rank_std: int  # Position rank in standard scoring leagues
    pts_half_ppr: float  # Points in half-point per reception fantasy leagues
    pts_ppr: float  # Points in point per reception fantasy leagues
    pts_std: float  # Points in standard scoring fantasy leagues
    rec: int  # Receptions made
    rec_0_4: int  # Receptions made between 0-4 yards
    rec_5_9: int  # Receptions made between 5-9 yards
    rec_10_19: int  # Receptions made between 10-19 yards
    rec_20_29: int  # Receptions made between 20-29 yards
    rec_30_39: int  # Receptions made between 30-39 yards
    rec_40p: int  # Receptions made over 40 yards
    rec_air_yd: int  # Air yards on receptions
    rec_drop: int  # Number of receptions dropped
    rec_fd: int  # Receiving first downs
    rec_lng: int  # Longest reception in yards
    rec_rz_tgt: int  # Receiving targets in the red zone
    rec_td: int  # Receiving touchdowns
    rec_td_lng: int  # Longest receiving touchdown
    rec_tgt: int  # Targets received
    rec_yac: int  # Receiving yards after contact
    rec_yar: int  # Receiving yards after reception
    rec_yd: int  # Total receiving yards
    rec_ypr: float  # Receiving yards per reception
    rec_ypt: float  # Receiving yards per target
    rush_att: int  # Rushing attempts
    rush_btkl: int  # Rushing attempts broken for tackles
    rush_fd: int  # Rushing first downs
    rush_lng: int  # Longest rush attempt in yards
    rush_rec_yd: int  # Combined rushing and receiving yards
    rush_rz_att: int  # Rushing attempts in the red zone
    rush_td: int  # Rushing touchdowns
    rush_td_lng: int  # Longest rushing touchdown
    rush_tkl_loss: int  # Number of times tackled for a loss on rush attempts
    rush_tkl_loss_yd: int  # Yards lost on tackles for a loss during rushing attempts
    rush_yac: int  # Rushing yards after contact
    rush_yd: int  # Total rushing yards
    rush_ypa: float  # Rushing yards per attempt
    tm_def_snp: int  # Number of snaps played on defense
    tm_off_snp: int  # Number of snaps played on offense
    tm_st_snp: int  # Number of snaps played on special teams

    def to_dict(self):
        return self.__dict__


from dataclasses import dataclass


@dataclass
class WideReceiverStats:
    anytime_tds: int  # Total touchdowns scored at any moment
    bonus_fd_wr: int  # Bonus points for wide receivers based on first downs
    bonus_rec_wr: int  # Bonus points for wide receivers based on receptions
    bonus_rec_yd_100: int  # Bonus for receiving 100 yards
    bonus_rush_rec_yd_100: int  # Bonus for rushing or receiving 100 yards
    fum: int  # Fumbles by the wide receiver
    fum_lost: int  # Fumbles lost by the wide receiver
    gp: int  # Games played
    gs: int  # Games started
    gms_active: int  # Games in which the player was active
    off_snp: int  # Number of offensive snaps
    penalty: int  # Penalties committed
    penalty_yd: int  # Yards lost due to penalties
    pos_rank_half_ppr: int  # Position rank in half-point per reception leagues
    pos_rank_ppr: int  # Position rank in point per reception leagues
    pos_rank_std: int  # Position rank in standard scoring leagues
    pts_half_ppr: float  # Points scored in half-point per reception leagues
    pts_ppr: float  # Points scored in point per reception leagues
    pts_std: float  # Points scored in standard scoring leagues
    rec: int  # Receptions made
    rec_0_4: int  # Receptions made between 0-4 yards
    rec_5_9: int  # Receptions made between 5-9 yards
    rec_10_19: int  # Receptions made between 10-19 yards
    rec_20_29: int  # Receptions made between 20-29 yards
    rec_30_39: int  # Receptions made between 30-39 yards
    rec_40p: int  # Receptions made over 40 yards
    rec_air_yd: int  # Air yards gained on receptions
    rec_drop: int  # Receptions dropped
    rec_fd: int  # Receiving first downs
    rec_lng: int  # Longest reception in yards
    rec_rz_tgt: int  # Receiving targets in the red zone
    rec_td: int  # Receiving touchdowns
    rec_td_lng: int  # Longest receiving touchdown
    rec_tgt: int  # Targets received
    rec_yar: int  # Receiving yards after the catch
    rec_yd: int  # Total receiving yards
    rec_ypr: float  # Receiving yards per reception
    rec_ypt: float  # Receiving yards per target
    rush_rec_yd: int  # Combined rushing and receiving yards
    st_snp: int  # Special teams snaps
    tm_def_snp: int  # Team defensive snaps
    tm_off_snp: int  # Team offensive snaps
    tm_st_snp: int  # Team special teams snaps
    idp_tkl: int  # Individual defensive player tackles
    idp_tkl_solo: int  # Individual defensive player solo tackles

    def to_dict(self):
        return self.__dict__
