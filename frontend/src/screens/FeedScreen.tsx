import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { submitFeedback } from '../api/feedback';
import { getItems } from '../api/items';
import { useSession } from '../auth/SessionProvider';
import { PrimaryButton } from '../components/PrimaryButton';
import { SwipeCard, type SwipeCardHandle } from '../components/SwipeCard';
import { colors } from '../theme';
import type { Feedback, FeedbackAction, SuggestorItem } from '../types';

type Status = 'loading' | 'error' | 'ready';

export function FeedScreen() {
  const { signOut } = useSession();
  const [status, setStatus] = useState<Status>('loading');
  const [items, setItems] = useState<SuggestorItem[]>([]);
  const [index, setIndex] = useState(0);
  // Every swipe this session, oldest first. Kept across "Start over".
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const topCard = useRef<SwipeCardHandle>(null);

  const load = useCallback(() => {
    getItems()
      .then((loaded) => {
        setItems(loaded);
        setIndex(0);
        setStatus('ready');
      })
      .catch((err) => {
        console.warn('[getItems] failed', err);
        setStatus('error');
      });
  }, []);

  useEffect(load, [load]);

  const reload = () => {
    setStatus('loading');
    load();
  };

  const handleSwipe = (itemId: number, action: FeedbackAction) => {
    const record: Feedback = { itemId, action, timestamp: new Date().toISOString() };
    setFeedback((prev) => [...prev, record]);
    setIndex((i) => i + 1);
    submitFeedback(record).catch((err) => console.warn('[submitFeedback] failed', err));
  };

  const top = items[index];
  const next = items[index + 1];

  let content;
  if (status === 'loading') {
    content = (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  } else if (status === 'error') {
    content = (
      <View style={styles.centered}>
        <Text style={styles.messageTitle}>Couldn't load places</Text>
        <Text style={styles.messageBody}>Check your connection and try again.</Text>
        <PrimaryButton label="Try again" onPress={reload} style={styles.messageAction} />
      </View>
    );
  } else if (!top) {
    const likes = feedback.filter((f) => f.action === 'like').length;
    content = (
      <View style={styles.centered}>
        <Text style={styles.messageTitle}>You're all caught up</Text>
        <Text style={styles.messageBody}>
          {likes} liked, {feedback.length - likes} passed this session.
        </Text>
        <PrimaryButton label="Start over" onPress={reload} style={styles.messageAction} />
      </View>
    );
  } else {
    content = (
      <>
        <View style={styles.deck}>
          {next && <SwipeCard key={next.id} item={next} isTop={false} onSwipe={handleSwipe} />}
          <SwipeCard key={top.id} ref={topCard} item={top} isTop onSwipe={handleSwipe} />
        </View>
        <View style={styles.buttons}>
          <RoundButton
            label="Dislike"
            icon="✕"
            color={colors.dislike}
            onPress={() => topCard.current?.swipe('dislike')}
          />
          <RoundButton
            label="Like"
            icon="♥"
            color={colors.like}
            onPress={() => topCard.current?.swipe('like')}
          />
        </View>
      </>
    );
  }

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.column}>
        <View style={styles.header}>
          <Text style={styles.brand}>Suggestor</Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Sign out"
            onPress={signOut}
            hitSlop={8}
            style={({ pressed }) => pressed && styles.pressed}
          >
            <Text style={styles.signOut}>Sign out</Text>
          </Pressable>
        </View>
        {content}
      </View>
    </SafeAreaView>
  );
}

function RoundButton(props: { label: string; icon: string; color: string; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.label}
      onPress={props.onPress}
      style={({ pressed }) => [
        styles.roundButton,
        { borderColor: props.color },
        pressed && styles.pressed,
      ]}
    >
      <Text style={[styles.roundButtonIcon, { color: props.color }]}>{props.icon}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  column: {
    flex: 1,
    width: '100%',
    maxWidth: 440,
    alignSelf: 'center',
    paddingHorizontal: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  brand: {
    fontSize: 24,
    fontWeight: '800',
    color: colors.primary,
  },
  signOut: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.textMuted,
  },
  deck: {
    flex: 1,
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 40,
    paddingVertical: 20,
  },
  roundButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.card,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  roundButtonIcon: {
    fontSize: 28,
    fontWeight: '700',
  },
  pressed: {
    opacity: 0.6,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    padding: 24,
  },
  messageTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.text,
    textAlign: 'center',
  },
  messageBody: {
    fontSize: 16,
    color: colors.textMuted,
    textAlign: 'center',
  },
  messageAction: {
    marginTop: 8,
  },
});
