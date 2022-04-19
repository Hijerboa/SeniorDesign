import numpy as np
from db.database_connection import create_session
from db.models import Tweet, TwitterUser, CongressMemberData, Bill

CONF_THRESHOLD = 0.7
NEG_THRESHOLD = -0.33
POS_THRESHOLD = 0.33

politician_usernames = ['RepAdams', 'Robert_Aderholt', 'RepPeteAguilar', 'RepRickAllen', 'RepColinAllred',
                        'MarkAmodeiNV2', 'RepArmstrongND', 'RepArrington', 'RepAuchincloss', 'RepCindyAxne',
                        'RepBrianBabin', 'RepDonBacon', 'RepJimBaird', 'RepBalderson', 'RepJimBanks', 'RepAndyBarr',
                        'RepBarragan', 'RepKarenBass', 'RepBeatty', 'RepBentz', 'RepBera', 'RepJackBergman',
                        'RepDonBeyer', 'RepBice', 'RepAndyBiggsAZ', 'RepGusBilirakis', 'SanfordBishop', 'RepDanBishop',
                        'repblumenauer', 'RepLBR', 'RepBoebert', 'RepBonamici', 'RepBost', 'RepBourdeaux', 'RepBowman',
                        'CongBoyle', 'RepKevinBrady', 'RepMoBrooks', 'RepAnthonyBrown', 'RepShontelBrown',
                        'RepBrownley', 'VernBuchanan', 'RepKenBuck', 'RepLarryBucshon', 'RepTedBudd', 'RepTimBurchett',
                        'michaelcburgess', 'RepCori', 'RepCheri', 'GKButterfield', 'KenCalvert', 'RepKatCammack',
                        'RepCarbajal', 'RepCardenas', 'RepMikeCarey', 'RepJerryCarl', 'RepAndreCarson',
                        'RepBuddyCarter', 'JudgeCarter', 'RepTroyCarter', 'RepCartwright', 'RepEdCase',
                        'RepCasten', 'USRepKCastor', 'JoaquinCastrotx', 'RepCawthorn', 'RepSteveChabot',
                        'RepLizCheney', 'CongresswomanSC', 'RepJudyChu', 'RepCicilline', 'RepKClark',
                        'RepYvetteClarke', 'repcleaver', 'RepBenCline', 'RepCloudTX', 'WhipClyburn',
                        'Rep_Clyde ', 'RepCohen', 'TomColeOK04', 'RepJamesComer', 'GerryConnolly',
                        'repjimcooper', 'RepLouCorrea', 'RepJimCosta', 'RepJoeCourtney', 'RepAngieCraig',
                        'RepRickCrawford', 'RepDanCrenshaw', 'RepCharlieCrist', 'RepJasonCrow', 'RepCuellar',
                        'RepJohnCurtis', 'RepDavids', 'WarrenDavidson', 'RepDannyDavis', 'RodneyDavis', 'RepDean',
                        'RepPeterDeFazio', 'RepDianaDeGette', 'rosadelauro', 'RepDelBene', 'repdelgado',
                        'RepValDemings', 'RepDeSaulnier', 'DesJarlaisTN04', 'RepTedDeutch', 'MarioDB', 'RepDebDingell',
                        'RepLloydDoggett', 'RepDonaldsPress', 'USRepMikeDoyle', 'RepJeffDuncan', 'DrNealDunnFL2',
                        'RepEllzey', 'RepTomEmmer', 'RepEscobar', 'RepAnnaEshoo', 'RepEspaillat', 'RepRonEstes',
                        'RepDwightEvans', 'RepPatFallon', 'RepFeenstra', 'RepDrewFerguson', 'RepFischbach', 'RepFitzgerald', 'RepBrianFitz', 'RepChuck', 'RepFletcher', 'RepBillFoster', 'virginiafoxx', 'RepLoisFrankel', 'RepFranklin', 'RepRussFulcher', 'RepMattGaetz', 'RepGallagher', 'RepRubenGallego', 'RepGaramendi', 'RepGarbarino', 'RepChuyGarcia', 'RepMikeGarcia', 'RepSylviaGarcia', 'RepBobGibbs', 'RepCarlos', 'replouiegohmert', 'RepGolden', 'RepJimmyGomez', 'RepTonyGonzales', 'RepJenniffer', 'RepAGonzalez', 'RepGonzalez', 'RepBobGood', 'Lancegooden', 'RepGosar', 'RepJoshG', 'RepKayGranger', 'RepGarretGraves', 'RepSamGraves', 'RepAlGreen', 'RepMarkGreen', 'RepMTG', 'RepMGriffith', 'RepRaulGrijalva', 'RepGrothman', 'RepMichaelGuest', 'RepGuthrie', 'RepJoshHarder', 'RepAndyHarrisMD', 'RepHarshbarger', 'RepHartzler', 'RepJahanaHayes', 'repkevinhern', 'RepHerrell', 'HerreraBeutler', 'CongressmanHice', 'RepBrianHiggins', 'RepClayHiggins', 'RepFrenchHill', 'jahimes', 'RepAshleyHinson', 'RepTrey', 'RepHorsford', 'RepHoulahan', 'LeaderHoyer', 'RepRichHudson', 'RepHuffman', 'RepHuizenga', 'repdarrellissa', 'JacksonLeeTX18', 'RepRonnyJackson', 'RepJacobs', 'RepSaraJacobs', 'RepJayapal', 'RepJeffries', 'RepBillJohnson', 'RepDustyJohnson', 'RepEBJ', 'RepHankJohnson', 'RepMikeJohnson', 'RepMondaire', 'Jim_Jordan', 'RepDaveJoyce', 'RepJohnJoyce', 'KaheleRep', 'RepMarcyKaptur', 'RepJohnKatko', 'USRepKeating', 'RepFredKeller', 'MikeKellyPA', 'RepRobinKelly', 'RepTrentKelly', 'RepRoKhanna', 'RepDanKildee', 'RepDerekKilmer', 'RepAndyKimNJ', 'RepYoungKim', 'RepRonKind', 'RepKinzinger', 'RepKirkpatrick', 'CongressmanRaja', 'RepAnnieKuster', 'RepDavidKustoff', 'RepLaHood', 'RepLaMalfa', 'RepConorLamb', 'RepDLamborn', 'JimLangevin', 'RepRickLarsen', 'RepJohnLarson', 'boblatta', 'RepLaTurner', 'RepLawrence', 'RepAlLawsonJr', 'RepBarbaraLee', 'RepSusieLee', 'RepTeresaLF', 'RepDLesko', 'RepJuliaLetlow', 'RepAndyLevin', 'RepMikeLevin', 'RepTedLieu', 'RepZoeLofgren', 'USRepLong', 'RepLoudermilk', 'RepLowenthal', 'RepFrankLucas', 'RepBlaine', 'RepElaineLuria', 'RepStephenLynch', 'RepNancyMace', 'RepMalinowski', 'RepMalliotakis', 'RepMaloney', 'RepSeanMaloney', 'RepMann', 'RepKManning', 'RepThomasMassie', 'RepBrianMast', 'DorisMatsui', 'RepLucyMcBath', 'GOPLeader', 'RepMcCaul', 'RepLisaMcClain', 'RepMcClintock', 'BettyMcCollum04', 'RepMcEachin', 'RepMcGovern', 'PatrickMcHenry', 'RepMcKinley', 'RepMcNerney', 'RepGregoryMeeks', 'RepMeijer', 'RepGraceMeng', 'RepMeuser', 'RepKweisiMfume', 'RepMMM', 'RepCarolMiller', 'RepMaryMiller', 'RepMoolenaar', 'RepAlexMooney', 'RepBarryMoore', 'RepBlakeMoore', 'RepGwenMoore', 'RepJoeMorelle', 'teammoulton', 'RepMrvan', 'RepMullin', 'RepGregMurphy', 'RepStephMurphy', 'RepJerryNadler', 'gracenapolitano', 'RepRichardNeal', 'RepJoeNeguse', 'RepTroyNehls', 'RepNewhouse', 'RepMarieNewman', 'DonaldNorcross', 'RepRalphNorman', 'EleanorNorton', 'RepOHalleran', 'JayObernolte', 'RepAOC', 'Ilhan', 'RepBurgessOwens', 'CongPalazzo', 'FrankPallone', 'USRepGaryPalmer', 'RepJimmyPanetta', 'RepChrisPappas', 'BillPascrell', 'RepDonaldPayne', 'SpeakerPelosi', 'RepGregPence', 'RepPerlmutter', 'RepScottPerry', 'RepScottPeters', 'RepPfluger', 'RepDeanPhillips', 'chelliepingree', 'StaceyPlaskett', 'repmarkpocan', 'RepKatiePorter', 'congbillposey', 'RepPressley', 'RepDavidEPrice', 'RepMikeQuigley', 'RepAmata', 'RepRaskin', 'RepTomReed', 'GReschenthaler', 'RepKathleenRice', 'RepTomRice', 'cathymcmorris', 'RepHalRogers', 'RepMikeRogersAL', 'RepJohnRose', 'RepRosendale', 'RepDeborahRoss', 'RepDavidRouzer', 'RepChipRoy', 'RepRoybalAllard', 'RepRaulRuizMD', 'Call_Me_Dutch', 'RepBobbyRush', 'RepRutherfordFL', 'RepTimRyan', 'Kilili_Sablan', 'RepMariaSalazar', 'GuamCongressman', 'RepLindaSanchez', 'RepSarbanes', 'SteveScalise', 'RepMGS', 'janschakowsky', 'RepAdamSchiff', 'RepSchneider', 'RepSchrader', 'RepKimSchrier', 'RepDavid', 'AustinScottGA08', 'repdavidscott', 'BobbyScott', 'PeteSessions', 'RepTerriSewell', 'BradSherman', 'RepSherrill', 'CongMikeSimpson', 'RepSires', 'RepSlotkin', 'RepAdamSmith', 'RepAdrianSmith', 'RepJasonSmith', 'RepSmucker', 'RepDarrenSoto', 'RepSpanberger', 'RepSpartz', 'RepSpeier', 'Rep_Stansbury', 'RepGregStanton', 'RepPeteStauber', 'RepSteel', 'RepStefanik', 'RepBryanSteil', 'RepGregSteube', 'RepHaleyStevens', 'RepChrisStewart', 'RepStricklandWA', 'RepTomSuozzi', 'RepSwalwell', 'RepMarkTakano', 'RepVanTaylor', 'claudiatenney', 'BennieGThompson', 'CongressmanGT', 'RepThompson', 'RepTiffany', 'RepTimmons', 'repdinatitus', 'RepRashida', 'RepPaulTonko', 'NormaJTorres', 'RepRitchie', 'RepLoriTrahan', 'RepDavidTrone', 'RepMikeTurner', 'RepUnderwood', 'RepFredUpton', 'RepDavidValadao', 'RepBethVanDuyne', 'RepJuanVargas', 'RepVeasey', 'NydiaVelazquez', 'RepAnnWagner', 'RepWalberg', 'RepWalorski', 'michaelgwaltz', 'RepDWStweets', 'RepMaxineWaters', 'RepBonnie', 'TXRandy14', 'RepWebster', 'PeterWelch', 'RepBradWenstrup', 'RepWesterman', 'RepWexton', 'RepSusanWild', 'RepNikema', 'RepRWilliams', 'RepWilson', 'RepJoeWilson', 'RobWittman', 'rep_stevewomack', 'RepJohnYarmuth', 'RepLeeZeldin', 'SenatorBaldwin', 'SenJohnBarrasso', 'SenatorBennet', 'MarshaBlackburn', 'SenBlumenthal', 'RoyBlunt', 'CoryBooker', 'JohnBoozman', 'SenatorBraun', 'SenSherrodBrown', 'SenatorBurr', 'SenatorCantwell', 'SenCapito', 'SenatorCardin', 'SenatorCarper', 'SenBobCasey', 'SenBillCassidy', 'SenatorCollins', 'ChrisCoons', 'JohnCornyn', 'SenCortezMasto', 'SenTomCotton', 'SenKevinCramer', 'MikeCrapo', 'SenTedCruz', 'SteveDaines', 'SenDuckworth', 'SenatorDurbin', 'SenJoniErnst', 'SenFeinstein', 'SenatorFischer', 'SenGillibrand', 'LindseyGrahamSC', 'ChuckGrassley', 'SenatorHagerty', 'SenatorHassan', 'HawleyMO', 'MartinHeinrich', 'SenatorHick', 'maziehirono', 'SenJohnHoeven', 'SenHydeSmith', 'JimInhofe', 'SenRonJohnson', 'timkaine', 'SenMarkKelly', 'SenJohnKennedy', 'SenAngusKing', 'SenAmyKlobuchar', 'SenatorLankford', 'SenatorLeahy', 'SenMikeLee', 'SenatorLujan', 'SenLummis', 'Sen_JoeManchin', 'SenMarkey', 'SenatorMarshall', 'senatemajldr', 'SenatorMenendez', 'SenJeffMerkley', 'JerryMoran', 'lisamurkowski', 'ChrisMurphyCT', 'PattyMurray', 'ossoff', 'SenAlexPadilla', 'RandPaul', 'SenGaryPeters', 'senrobportman', 'SenJackReed', 'SenatorRisch', 'SenatorRomney', 'SenJackyRosen', 'SenatorRounds', 'marcorubio', 'SenSanders', 'SenSasse', 'SenBrianSchatz', 'SenSchumer', 'SenRickScott', 'SenatorTimScott', 'SenatorShaheen', 'SenShelby', 'SenatorSinema', 'SenTinaSmith', 'SenStabenow', 'SenDanSullivan', 'SenatorTester', 'SenJohnThune', 'SenThomTillis', 'SenToomey', 'SenTuberville', 'ChrisVanHollen', 'MarkWarner', 'SenatorWarnock', 'SenWarren', 'SenWhitehouse', 'SenatorWicker', 'RonWyden', 'SenToddYoung']

def get_tweets(bill_id: str):
    """Returns all tweets for a specified bill and their user objects

    Args:
        bill_id (str): Bill ID

    Returns:
        set(): Set of tuples
        Each tuple contains a tweet object and it's cooresponding user object
        
    Yes I know this is memory inefficient. It reduces database calls. I don't fucking care.
    """
    
    all_tweets = set()
    all_users = [] # Done as an array to play nice with SQLAlchemy
    users_dict = {}
    
    session = create_session(expire_on_commit=False)
    
    bill = session.query(Bill).filter(Bill.bill_id==bill_id).first()
    for phrase in bill.keywords:
        tweets = session.query(Tweet).where(Tweet.search_phrases.contains(phrase)).all()
        for tweet in tweets:
            if tweet not in all_tweets:
                all_tweets.add(tweet)
                if tweet.author_id not in all_users:
                    all_users.append(tweet.author_id)

    user_objects = session.query(TwitterUser).filter(TwitterUser.id.in_(all_users)).all()
    num_verified = 0
    num_politicians = 0
    for user_object in user_objects:
        users_dict[user_object.id] = user_object
        if user_object.verified:
            num_verified += 1
        if user_object.username in politician_usernames:
            num_politicians += 1
    
    tweet_users_tuples = set()
    for tweet in all_tweets:
        try:
            tuple = (tweet, users_dict[tweet.author_id])
        except KeyError:
            continue
        tweet_users_tuples.add(tuple)
    
    session.close()
    return tweet_users_tuples, {'num_users': len(user_objects), 'num_tweets': len(tweet_users_tuples), 'num_verified_users': num_verified, 'num_politicians_tweeting': num_politicians}


def get_flat_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
    
    for tuple in tweets:
        tweet = tuple[0] # Get the tweet from the tuple
        if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
            analyzed_tweets += 1
            if tweet.sentiment is None:
                continue
            if tweet.sentiment > POS_THRESHOLD:
                total_positive += 1
            elif tweet.sentiment < NEG_THRESHOLD:
                total_negative += 1
            else:
                total_neutral += 1
            
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }

    return results_dict


def verified_user_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
    
    for tuple in tweets:
        tweet = tuple[0]
        user = tuple[1]
        if user.verified:
            if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
                analyzed_tweets += 1
                if tweet.sentiment is None:
                    continue
                if tweet.sentiment > POS_THRESHOLD:
                    total_positive += 1
                elif tweet.sentiment < NEG_THRESHOLD:
                    total_negative += 1
                else:
                    total_neutral += 1
    
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }

    return results_dict


def politician_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
                
    
    for tuple in tweets:
        tweet = tuple[0]
        user = tuple[1]
        if user.username in politician_usernames:
            if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
                analyzed_tweets += 1
                if tweet.sentiment is None:
                    continue
                if tweet.sentiment > POS_THRESHOLD:
                    total_positive += 1
                elif tweet.sentiment < NEG_THRESHOLD:
                    total_negative += 1
                else:
                    total_neutral += 1
    
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }

    return results_dict


def more_than_average_likes(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    weighted_positive = 0
    weighted_neutral = 0
    weighted_negative = 0
    analyzed_tweets = 0
    
    likes = [tuple[0].likes for tuple in tweets]
        
    likes_mean = np.mean(likes)
    likes_std = np.std(likes)
    
    for tuple in tweets:
        tweet = tuple[0]
        weight = 1 + (tweet.likes - likes_mean) / likes_std
        if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
            analyzed_tweets += 1
            if tweet.sentiment is None:
                continue
            if tweet.sentiment > POS_THRESHOLD:
                total_positive += 1
                weighted_positive += 1 * weight
            elif tweet.sentiment < NEG_THRESHOLD:
                total_negative += 1
                weighted_negative += 1 * weight
            else:
                total_neutral += 1
                weighted_neutral += 1 * weight
                
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative,
        'weighted_positive': weighted_positive,
        'weighted_neutral': weighted_neutral,
        'weighted_negative': weighted_negative
    }

    return results_dict


def confidence_weighting(tweets):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    weighted_positive = 0
    weighted_negative = 0
    analyzed_tweets = 0
    
    for tuple in tweets:
        tweet = tuple[0]
        analyzed_tweets += 1
        if tweet.sentiment is None:
            continue
        if tweet.sentiment > POS_THRESHOLD:
            total_positive += 1
            weighted_positive += tweet.sentiment_confidence
        elif tweet.sentiment < NEG_THRESHOLD:
            total_negative += 1
            weighted_negative += tweet.sentiment_confidence
        else:
            total_neutral += 1
            
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative,
        'weighted_positive': weighted_positive,
        'weighted_negative': weighted_negative
    }

    return results_dict
            
