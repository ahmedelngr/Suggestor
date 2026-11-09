import { useEffect, useImperativeHandle, useRef, useState, type Ref } from 'react';
import { Animated, Dimensions, Image, PanResponder, StyleSheet, Text, View } from 'react-native';

import { colors } from '../theme';
import type { FeedbackAction, SuggestorItem } from '../types';

/** How far (px) the card must be dragged before letting go counts as a swipe. */
const SWIPE_THRESHOLD = 120;
const SWIPE_OUT_MS = 220;

// PanResponder runs in JS, so drags can't use the native driver. Keep every
// animation on the JS driver too: mixing drivers on one value throws.
const USE_NATIVE_DRIVER = false;

export interface SwipeCardHandle {
  /** Animates the card off screen as if it was swiped. Used by the buttons. */
  swipe: (action: FeedbackAction) => void;
}

interface Props {
  item: SuggestorItem;
  /** Only the top card can be dragged. */
  isTop: boolean;
  onSwipe: (itemId: number, action: FeedbackAction) => void;
  ref?: Ref<SwipeCardHandle>;
}

export function SwipeCard({ item, isTop, onSwipe, ref }: Props) {
  const [position] = useState(() => new Animated.ValueXY());
  const swiping = useRef(false);

  // The PanResponder is created once, so it reads the latest props via refs.
  const latest = useRef({ itemId: item.id, onSwipe });
  useEffect(() => {
    latest.current = { itemId: item.id, onSwipe };
  });

  const swipeOut = (action: FeedbackAction, dy = 0) => {
    if (swiping.current) return;
    swiping.current = true;
    const direction = action === 'like' ? 1 : -1;
    const x = direction * Dimensions.get('window').width * 1.5;
    Animated.timing(position, {
      toValue: { x, y: dy },
      duration: SWIPE_OUT_MS,
      useNativeDriver: USE_NATIVE_DRIVER,
    }).start(() => latest.current.onSwipe(latest.current.itemId, action));
  };

  const snapBack = () => {
    Animated.spring(position, {
      toValue: { x: 0, y: 0 },
      friction: 5,
      useNativeDriver: USE_NATIVE_DRIVER,
    }).start();
  };

  const [panResponder] = useState(() =>
    PanResponder.create({
      onStartShouldSetPanResponder: () => !swiping.current,
      onPanResponderMove: Animated.event([null, { dx: position.x, dy: position.y }], {
        useNativeDriver: USE_NATIVE_DRIVER,
      }),
      onPanResponderRelease: (_, gesture) => {
        if (gesture.dx > SWIPE_THRESHOLD) swipeOut('like', gesture.dy);
        else if (gesture.dx < -SWIPE_THRESHOLD) swipeOut('dislike', gesture.dy);
        else snapBack();
      },
      onPanResponderTerminationRequest: () => false,
      onPanResponderTerminate: snapBack,
    }),
  );

  useImperativeHandle(ref, () => ({ swipe: (action) => swipeOut(action) }));

  const rotate = position.x.interpolate({
    inputRange: [-200, 0, 200],
    outputRange: ['-12deg', '0deg', '12deg'],
  });
  // The stamp is fully visible exactly when letting go would count as a swipe.
  const likeOpacity = position.x.interpolate({
    inputRange: [0, SWIPE_THRESHOLD],
    outputRange: [0, 1],
    extrapolate: 'clamp',
  });
  const nopeOpacity = position.x.interpolate({
    inputRange: [-SWIPE_THRESHOLD, 0],
    outputRange: [1, 0],
    extrapolate: 'clamp',
  });

  return (
    <Animated.View
      style={[
        styles.card,
        { transform: [{ translateX: position.x }, { translateY: position.y }, { rotate }] },
      ]}
      {...(isTop ? panResponder.panHandlers : {})}
    >
      <View style={styles.inner}>
        <Image source={{ uri: item.imageUrl }} style={styles.image} resizeMode="cover" />
        <View style={styles.info}>
          <View style={styles.titleRow}>
            <Text style={styles.title} numberOfLines={1}>
              {item.title}
            </Text>
            <Text style={styles.distance}>{item.distance.toFixed(1)} mi</Text>
          </View>
          <Text style={styles.description} numberOfLines={3}>
            {item.description}
          </Text>
          <View style={styles.tags}>
            {item.tags.map((tag) => (
              <View key={tag} style={styles.chip}>
                <Text style={styles.chipText}>{tag}</Text>
              </View>
            ))}
          </View>
        </View>
      </View>

      <Animated.View style={[styles.stamp, styles.likeStamp, { opacity: likeOpacity }]}>
        <Text style={[styles.stampText, { color: colors.like }]}>LIKE</Text>
      </Animated.View>
      <Animated.View style={[styles.stamp, styles.nopeStamp, { opacity: nopeOpacity }]}>
        <Text style={[styles.stampText, { color: colors.dislike }]}>NOPE</Text>
      </Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    position: 'absolute',
    inset: 0,
    borderRadius: 16,
    backgroundColor: colors.card,
    boxShadow: '0 4px 14px rgba(0, 0, 0, 0.12)',
    // Stops text from being highlighted while dragging with a mouse on web.
    userSelect: 'none',
  },
  inner: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
  },
  image: {
    flex: 1,
    backgroundColor: colors.imagePlaceholder,
  },
  info: {
    padding: 16,
    gap: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    gap: 12,
  },
  title: {
    flex: 1,
    fontSize: 22,
    fontWeight: '700',
    color: colors.text,
  },
  distance: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.textMuted,
  },
  description: {
    fontSize: 15,
    lineHeight: 21,
    color: colors.textMuted,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  chip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: colors.chip,
  },
  chipText: {
    fontSize: 13,
    color: colors.text,
  },
  stamp: {
    position: 'absolute',
    top: 32,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 4,
    borderRadius: 8,
    pointerEvents: 'none',
  },
  likeStamp: {
    left: 24,
    borderColor: colors.like,
    transform: [{ rotate: '-15deg' }],
  },
  nopeStamp: {
    right: 24,
    borderColor: colors.dislike,
    transform: [{ rotate: '15deg' }],
  },
  stampText: {
    fontSize: 32,
    fontWeight: '800',
    letterSpacing: 2,
  },
});
