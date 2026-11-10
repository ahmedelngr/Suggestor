import { router } from 'expo-router';
import { useCallback, useEffect, useState, type ReactNode } from 'react';
import {
  ActivityIndicator,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { getLikes } from '../api/feedback';
import { getProfile } from '../api/profile';
import { useSession } from '../auth/SessionProvider';
import { Avatar } from '../components/Avatar';
import { PrimaryButton } from '../components/PrimaryButton';
import { colors } from '../theme';
import type { LikedItem, UserProfile } from '../types';

type Status = 'loading' | 'error' | 'ready';

interface ProfileData {
  profile: UserProfile;
  likes: LikedItem[];
}

/** How many of the most common tags among the user's likes to show. */
const FAVORITE_TAG_COUNT = 5;

export function ProfileScreen() {
  const { session, signOut } = useSession();
  const [status, setStatus] = useState<Status>('loading');
  const [data, setData] = useState<ProfileData>();

  const load = useCallback(() => {
    // Null only for a moment while signing out, before the guard leaves this screen.
    if (!session) return;
    Promise.all([getProfile(session), getLikes(session)])
      .then(([profile, likes]) => {
        setData({ profile, likes });
        setStatus('ready');
      })
      .catch((err) => {
        console.warn('[profile] failed to load', err);
        setStatus('error');
      });
  }, [session]);

  useEffect(load, [load]);

  const reload = () => {
    setStatus('loading');
    load();
  };

  // Opening /profile directly on web leaves nothing to go back to.
  const goBack = () => (router.canGoBack() ? router.back() : router.replace('/'));

  let content;
  if (status === 'error') {
    content = (
      <View style={styles.centered}>
        <Text style={styles.messageTitle}>Couldn't load your profile</Text>
        <Text style={styles.messageBody}>Check your connection and try again.</Text>
        <PrimaryButton label="Try again" onPress={reload} style={styles.messageAction} />
      </View>
    );
  } else if (status === 'loading' || !data) {
    content = (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  } else {
    const { profile, likes } = data;
    const fullName = [profile.firstName, profile.lastName].filter(Boolean).join(' ') || profile.email;
    const favoriteTags = mostCommonTags(likes, FAVORITE_TAG_COUNT);

    content = (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.identity}>
          <Avatar name={fullName} size={88} />
          <Text style={styles.name}>{fullName}</Text>
          <Text style={styles.email}>{profile.email}</Text>
        </View>

        {favoriteTags.length > 0 && (
          <Section title="Favorite tags" note="From the places you liked">
            <View style={styles.tags}>
              {favoriteTags.map((tag) => (
                <View key={tag} style={styles.chip}>
                  <Text style={styles.chipText}>{tag}</Text>
                </View>
              ))}
            </View>
          </Section>
        )}

        <Section title={`Liked places (${likes.length})`}>
          {likes.length === 0 ? (
            <Text style={styles.emptyText}>
              No likes yet. Swipe right on places you'd try and they'll show up here.
            </Text>
          ) : (
            likes.map((liked, i) => (
              <LikedRow key={liked.item.id} liked={liked} divider={i > 0} />
            ))
          )}
        </Section>

        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Sign out"
          onPress={signOut}
          style={({ pressed }) => [styles.signOutButton, pressed && styles.pressed]}
        >
          <Text style={styles.signOutText}>Sign out</Text>
        </Pressable>
      </ScrollView>
    );
  }

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.column}>
        <View style={styles.header}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Back"
            onPress={goBack}
            hitSlop={8}
            style={({ pressed }) => pressed && styles.pressed}
          >
            <Text style={styles.back}>‹ Back</Text>
          </Pressable>
          <Text style={styles.headerTitle}>Profile</Text>
        </View>
        {content}
      </View>
    </SafeAreaView>
  );
}

function Section(props: { title: string; note?: string; children: ReactNode }) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeading}>
        <Text style={styles.sectionTitle}>{props.title}</Text>
        {props.note ? <Text style={styles.sectionNote}>{props.note}</Text> : null}
      </View>
      <View style={styles.sectionCard}>{props.children}</View>
    </View>
  );
}

function LikedRow({ liked, divider }: { liked: LikedItem; divider: boolean }) {
  const { item } = liked;
  const likedOn = new Date(liked.likedAt).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });

  return (
    <View style={[styles.likedRow, divider && styles.divider]}>
      <Image source={{ uri: item.imageUrl }} style={styles.thumbnail} resizeMode="cover" />
      <View style={styles.likedInfo}>
        <Text style={styles.likedTitle} numberOfLines={1}>
          {item.title}
        </Text>
        <Text style={styles.likedMeta} numberOfLines={1}>
          {item.tags.slice(0, 2).join(' · ')} · {item.distance.toFixed(1)} mi
        </Text>
      </View>
      <Text style={styles.likedDate}>{likedOn}</Text>
    </View>
  );
}

/** Tags that appear most often across the liked places. Ties keep the newest like first. */
function mostCommonTags(likes: LikedItem[], count: number): string[] {
  const counts = new Map<string, number>();
  for (const { item } of likes) {
    for (const tag of item.tags) counts.set(tag, (counts.get(tag) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, count)
    .map(([tag]) => tag);
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
    gap: 16,
    paddingVertical: 12,
  },
  back: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: colors.text,
  },
  pressed: {
    opacity: 0.6,
  },
  scrollContent: {
    gap: 24,
    paddingTop: 8,
    paddingBottom: 32,
  },
  identity: {
    alignItems: 'center',
    gap: 4,
  },
  name: {
    marginTop: 8,
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
    textAlign: 'center',
  },
  email: {
    fontSize: 15,
    color: colors.textMuted,
    textAlign: 'center',
  },
  section: {
    gap: 8,
  },
  sectionHeading: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    gap: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
  },
  sectionNote: {
    fontSize: 13,
    color: colors.textMuted,
  },
  sectionCard: {
    padding: 12,
    borderRadius: 16,
    backgroundColor: colors.card,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
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
  emptyText: {
    padding: 8,
    fontSize: 15,
    lineHeight: 21,
    color: colors.textMuted,
    textAlign: 'center',
  },
  likedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  divider: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  thumbnail: {
    width: 56,
    height: 56,
    borderRadius: 10,
    backgroundColor: colors.imagePlaceholder,
  },
  likedInfo: {
    flex: 1,
    gap: 2,
  },
  likedTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  likedMeta: {
    fontSize: 13,
    color: colors.textMuted,
  },
  likedDate: {
    fontSize: 13,
    color: colors.textMuted,
  },
  signOutButton: {
    minHeight: 50,
    borderRadius: 999,
    borderWidth: 1.5,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.card,
  },
  signOutText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.dislike,
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
